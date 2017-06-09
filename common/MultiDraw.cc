#include "MultiDraw.h"

#include "TFile.h"

#include <stdexcept>
#include <cstring>
#include <iostream>

Int_t
TTreeFormulaCached::GetNdata()
{
  if (fNdataCache < 0) {
    fNdataCache = TTreeFormula::GetNdata();
    fCache.assign(fNdataCache, std::pair<Bool_t, Double_t>(false, 0.));
  }

  return fNdataCache;
}

Double_t
TTreeFormulaCached::EvalInstance(Int_t _i, char const* _stringStack[]/* = 0*/)
{
  if (_i >= int(fCache.size()))
    return 0.;

  if (!fCache[_i].first) {
    fCache[_i].first = true;
    fCache[_i].second = TTreeFormula::EvalInstance(_i, _stringStack);
  }

  return fCache[_i].second;
}


ExprFiller::ExprFiller(TTreeFormula* _cuts/* = 0*/, TTreeFormula* _reweight/* = 0*/) :
  cuts_(_cuts),
  reweight_(_reweight)
{
}

ExprFiller::ExprFiller(ExprFiller const& _orig) :
  ownFormulas_(_orig.ownFormulas_)
{
  if (ownFormulas_) {
    for (unsigned iD(0); iD != _orig.getNdim(); ++iD) {
      auto& oexpr(*_orig.getExpr(iD));
      exprs_.push_back(new TTreeFormula(oexpr.GetName(), oexpr.GetTitle(), oexpr.GetTree()));
    }

    if (_orig.cuts_)
      cuts_ = new TTreeFormula(_orig.cuts_->GetName(), _orig.cuts_->GetTitle(), _orig.cuts_->GetTree());

    if (_orig.reweight_)
      reweight_ = new TTreeFormula(_orig.reweight_->GetName(), _orig.reweight_->GetTitle(), _orig.reweight_->GetTree());
  }
  else {
    exprs_ = _orig.exprs_;
    cuts_ = _orig.cuts_;
    reweight_ = _orig.reweight_;
  }
}

ExprFiller::~ExprFiller()
{
  if (ownFormulas_) {
    delete cuts_;
    delete reweight_;

    for (auto* expr : exprs_)
      delete expr;
  }
}

void
ExprFiller::updateTree()
{
  for (auto* expr : exprs_)
    expr->UpdateFormulaLeaves();

  if (cuts_)
    cuts_->UpdateFormulaLeaves();

  if (reweight_)
    reweight_->UpdateFormulaLeaves();
}

void
ExprFiller::fill(double _weight, std::vector<bool> const* _presel/* = 0*/)
{
  // using the first expr for the number of instances
  unsigned nD(exprs_.at(0)->GetNdata());
  // need to call GetNdata before EvalInstance
  if (cuts_)
    cuts_->GetNdata();

  if (printLevel_ > 3)
    std::cout << "          " << getObj()->GetName() << "::fill(" << _weight << ") => " << nD << " iterations" << std::endl;

  if (_presel && _presel->size() < nD)
    nD = _presel->size();

  bool loaded(false);

  for (unsigned iD(0); iD != nD; ++iD) {
    if (_presel && !(*_presel)[iD])
      continue;

    if (cuts_ && cuts_->EvalInstance(iD) == 0.)
      continue;

    ++counter_;

    if (!loaded) {
      for (unsigned iE(0); iE != exprs_.size(); ++iE) {
        exprs_[iE]->GetNdata();
        if (iD != 0) // need to always call EvalInstance(0)
          exprs_[iE]->EvalInstance(0);
      }
      if (reweight_) {
        reweight_->GetNdata();
        if (iD != 0)
          reweight_->EvalInstance(0);
      }
    }

    entryWeight_ = _weight;
    if (reweight_)
      entryWeight_ *= reweight_->EvalInstance(iD);

    doFill_(iD);

    loaded = true;
  }
}


Plot::Plot(TH1& _hist, TTreeFormula& _expr, TTreeFormula* _cuts/* = 0*/, TTreeFormula* _reweight/* = 0*/) :
  ExprFiller(_cuts, _reweight),
  hist_(&_hist)
{
  exprs_.push_back(&_expr);
}

Plot::Plot(Plot const& _orig) :
  ExprFiller(_orig),
  hist_(_orig.hist_)
{
}

void
Plot::doFill_(unsigned _iD)
{
  if (printLevel_ > 3)
    std::cout << "            Fill(" << exprs_[0]->EvalInstance(_iD) << "; " << entryWeight_ << ")" << std::endl;

  hist_->Fill(exprs_[0]->EvalInstance(_iD), entryWeight_);
}


Tree::Tree(TTree& _tree, TTreeFormula* _cuts/* = 0*/, TTreeFormula* _reweight/* = 0*/) :
  ExprFiller(_cuts, _reweight),
  tree_(&_tree)
{
  tree_->Branch("weight", &entryWeight_, "weight/D");

  bvalues_.reserve(NBRANCHMAX);
}

Tree::Tree(Tree const& _orig) :
  ExprFiller(_orig),
  tree_(_orig.tree_),
  bvalues_(_orig.bvalues_)
{
  tree_->SetBranchAddress("weight", &entryWeight_);

  bvalues_.reserve(NBRANCHMAX);

  // rely on the fact that the branch order should be aligned
  auto* branches(tree_->GetListOfBranches());
  for (int iB(0); iB != branches->GetEntries(); ++iB)
    tree_->SetBranchAddress(branches->At(iB)->GetName(), &bvalues_[iB]);
}

void
Tree::addBranch(char const* _bname, TTreeFormula& _expr)
{
  if (bvalues_.size() == NBRANCHMAX)
    throw std::runtime_error("Cannot add any more branches");

  bvalues_.resize(bvalues_.size() + 1);
  tree_->Branch(_bname, &bvalues_.back(), TString::Format("%s/D", _bname));

  exprs_.push_back(&_expr);
}

void
Tree::doFill_(unsigned _iD)
{
  if (printLevel_ > 3)
    std::cout << "            Fill(";

  for (unsigned iE(0); iE != exprs_.size(); ++iE) {
    if (printLevel_ > 3) {
      std::cout << exprs_[iE]->EvalInstance(_iD);
      if (iE != exprs_.size() - 1)
        std::cout << ", ";
    }

    bvalues_[iE] = exprs_[iE]->EvalInstance(_iD);
  }

  if (printLevel_ > 3)
    std::cout << "; " << entryWeight_ << ")" << std::endl;

  tree_->Fill();
}


MultiDraw::MultiDraw(char const* _path/* = ""*/) :
  tree_("events"),
  weightBranchName_("weight")
{
  if (_path && std::strlen(_path) != 0)
    tree_.Add(_path);
}

MultiDraw::~MultiDraw()
{
  for (auto* plots : {&postFull_, &postBase_, &unconditional_}) {
    for (auto* plot : *plots)
      delete plot;
  }

  for (auto& ff : library_)
    delete ff.second;
}

void
MultiDraw::setBaseSelection(char const* _cuts)
{
  if (!_cuts || std::strlen(_cuts) == 0) {
    delete baseSelection_;
    baseSelection_ = 0;
    return;
  }

  delete baseSelection_;

  baseSelection_ = new TTreeFormulaCached("baseSelection", _cuts, &tree_);
  library_.emplace(_cuts, baseSelection_);
}

void
MultiDraw::setFullSelection(char const* _cuts)
{
  if (!_cuts || std::strlen(_cuts) == 0) {
    delete fullSelection_;
    fullSelection_ = 0;
    return;
  }

  delete fullSelection_;

  fullSelection_ = new TTreeFormulaCached("fullSelection", _cuts, &tree_);
  library_.emplace(_cuts, fullSelection_);
}

void
MultiDraw::addPlot(TH1* _hist, char const* _expr, char const* _cuts/* = ""*/, bool _applyBaseline/* = true*/, bool _applyFullSelection/* = false*/, char const* _reweight/* = ""*/)
{
  TTreeFormulaCached* exprFormula(getFormula_(_expr));

  auto newPlot([_hist, exprFormula](TTreeFormula* _cutsFormula, TTreeFormula* _reweightFormula)->ExprFiller* {
      return new Plot(*_hist, *exprFormula, _cutsFormula, _reweightFormula);
    });

  if (printLevel_ > 1) {
    std::cout << "Adding Plot " << _hist->GetName() << " with expression " << _expr << std::endl;
    if (_cuts && std::strlen(_cuts) != 0)
      std::cout << " Cuts: " << _cuts << std::endl;
    if (_reweight && std::strlen(_reweight) != 0)
      std::cout << " Reweight: " << _reweight << std::endl;
  }

  addObj_(_cuts, _applyBaseline, _applyFullSelection, _reweight, newPlot);
}

void
MultiDraw::addTree(TTree* _tree, char const* _cuts/* = ""*/, bool _applyBaseline/* = true*/, bool _applyFullSelection/* = false*/, char const* _reweight/* = ""*/)
{
  auto newTree([_tree](TTreeFormula* _cutsFormula, TTreeFormula* _reweightFormula)->ExprFiller* {
      return new Tree(*_tree, _cutsFormula, _reweightFormula);
    });

  if (printLevel_ > 1) {
    std::cout << "Adding Tree " << _tree->GetName() << std::endl;
    if (_cuts && std::strlen(_cuts) != 0)
      std::cout << " Cuts: " << _cuts << std::endl;
    if (_reweight && std::strlen(_reweight) != 0)
      std::cout << " Reweight: " << _reweight << std::endl;
  }

  addObj_(_cuts, _applyBaseline, _applyFullSelection, _reweight, newTree);
}

void
MultiDraw::addTreeBranch(TTree* _tree, char const* _bname, char const* _expr)
{
  auto* exprFormula(getFormula_(_expr));

  for (auto* plots : {&postFull_, &postBase_, &unconditional_}) {
    for (auto* plot : *plots) {
      if (plot->getObj() == _tree) {
        if (printLevel_ > 1)
          std::cout << "Adding a branch " << _bname << " to tree " << plot->getObj()->GetName() << " with expression " << _expr << std::endl;

        static_cast<Tree*>(plot)->addBranch(_bname, *exprFormula);
      }
    }
  }
}

void
MultiDraw::addObj_(char const* _cuts, bool _applyBaseline, bool _applyFullSelection, char const* _reweight, ObjGen const& _gen)
{
  TTreeFormulaCached* cutsFormula(0);
  if (_cuts && std::strlen(_cuts) != 0)
    cutsFormula = getFormula_(_cuts);

  TTreeFormulaCached* reweightFormula(0);
  if (_reweight && std::strlen(_reweight) != 0)
    reweightFormula = getFormula_(_reweight);

  std::vector<ExprFiller*>* stack(0);
  if (_applyBaseline) {
    if (_applyFullSelection)
      stack = &postFull_;
    else
      stack = &postBase_;
  }
  else
    stack = &unconditional_;

  stack->push_back(_gen(cutsFormula, reweightFormula));
}

TTreeFormulaCached*
MultiDraw::getFormula_(char const* _expr)
{
  auto fItr(library_.find(_expr));
  if (fItr != library_.end())
    return fItr->second;

  auto* f(new TTreeFormulaCached("formula", _expr, &tree_));
  library_.emplace(_expr, f);

  return f;
}

void
MultiDraw::fillPlots(long _nEntries/* = -1*/)
{
  float weight(1.);
  unsigned eventNumber;

  // Turn off all branches first
  tree_.SetBranchStatus("*", false);

  // Turn on the necessary branches
  if (weightBranchName_.Length() != 0) {
    tree_.SetBranchStatus(weightBranchName_, true);
    tree_.SetBranchAddress(weightBranchName_, &weight);
  }
  if (prescale_ != 1) {
    tree_.SetBranchStatus("eventNumber", true);
    tree_.SetBranchAddress("eventNumber", &eventNumber);
  }
  // Branches used by the formulas
  for (auto& ff : library_) {
    for (auto* l : *ff.second->GetLeaves()) {
      if (printLevel_ > 1)
        std::cout << "Turning on branch " << static_cast<TLeaf*>(l)->GetBranch()->GetName() << std::endl;

      tree_.SetBranchStatus(static_cast<TLeaf*>(l)->GetBranch()->GetName(), true);
    }
  }

  for (auto* plots : {&postFull_, &postBase_, &unconditional_}) {
    for (auto* plot : *plots) {
      plot->setPrintLevel(printLevel_);
      plot->resetCount();
    }
  }

  std::vector<bool>* baseResults(0);
  std::vector<bool>* fullResults(0);

  if (baseSelection_ && baseSelection_->GetMultiplicity() != 0) {
    if (printLevel_ > 1)
      std::cout << "Base selection is based on an array." << std::endl;

    baseResults = new std::vector<bool>;
  }
  if (fullSelection_ && fullSelection_->GetMultiplicity() != 0) {
    if (printLevel_ > 1)
      std::cout << "Full selection is based on an array." << std::endl;

    fullResults = new std::vector<bool>;
  }

  long printEvery(0);
  if (printLevel_ == 1)
    printEvery = 10000;
  else if (printLevel_ == 2)
    printEvery = 100;
  else if (printLevel_ >= 3)
    printEvery = 1;

  long iEntry(0);
  int treeNumber(-1);
  unsigned passBase(0);
  unsigned passFull(0);
  while (iEntry != _nEntries && tree_.GetEntry(iEntry++) > 0) {
    if (printLevel_ >= 0 && iEntry % printEvery == 1) {
      std::cout << "\r      " << iEntry << " events";
      if (printLevel_ > 1)
        std::cout << std::endl;
    }

    if (prescale_ != 1 && eventNumber % prescale_ != 0)
      continue;

    if (treeNumber != tree_.GetTreeNumber()) {
      if (printLevel_ > 1)
        std::cout << "      Opened a new file: " << tree_.GetCurrentFile()->GetName() << std::endl;

      treeNumber = tree_.GetTreeNumber();

      if (baseSelection_)
        baseSelection_->UpdateFormulaLeaves();
      if (fullSelection_)
        fullSelection_->UpdateFormulaLeaves();
      for (auto* plot : unconditional_)
        plot->updateTree();
      for (auto* plot : postBase_)
        plot->updateTree();
      for (auto* plot : postFull_)
        plot->updateTree();
    }

    // Reset formula cache
    for (auto& ff : library_)
      ff.second->ResetCache();

    double eventWeight(weight * lumi_);

    // Plots that do not require passing the baseline cut
    for (auto* plot : unconditional_) {
      if (printLevel_ > 3)
        std::cout << "        Filling " << plot->getObj()->GetName() << std::endl;

      plot->fill(eventWeight);
    }

    // Baseline cut
    if (baseSelection_) {
      unsigned nD(baseSelection_->GetNdata());

      if (printLevel_ > 2)
        std::cout << "        Base selection has " << nD << " iterations" << std::endl;

      bool any(false);

      if (baseResults)
        baseResults->assign(nD, false);

      for (unsigned iD(0); iD != nD; ++iD) {
        if (baseSelection_->EvalInstance(iD) != 0.) {
          any = true;

          if (printLevel_ > 2)
            std::cout << "        Base selection " << iD << " is true" << std::endl;

          if (baseResults)
            (*baseResults)[iD] = true;
          else
            break; // no need to evaluate more
        }
      }

      if (!any)
        continue;
    }

    ++passBase;

    // Plots that require passing the baseline cut but not the full cut
    for (auto* plot : postBase_) {
      if (printLevel_ > 3)
        std::cout << "        Filling " << plot->getObj()->GetName() << std::endl;

      plot->fill(eventWeight, baseResults);
    }

    // Full cut
    if (fullSelection_) {
      unsigned nD(fullSelection_->GetNdata());

      if (printLevel_ > 2)
        std::cout << "        Full selection has " << nD << " iterations" << std::endl;

      bool any(false);

      if (fullResults)
        fullResults->assign(nD, false);

      if (baseResults && baseResults->size() < nD) {
        // fullResults for iD >= baseResults->size() will never be true
        nD = baseResults->size();
      }

      for (unsigned iD(0); iD != nD; ++iD) {
        if (baseResults && !(*baseResults)[iD])
          continue;

        if (fullSelection_->EvalInstance(iD) != 0.) {
          any = true;

          if (printLevel_ > 2)
            std::cout << "        Full selection " << iD << " is true" << std::endl;

          if (fullResults)
            (*fullResults)[iD] = true;
          else
            break;
        }
      }

      if (!any)
        continue;
    }

    ++passFull;

    // Plots that require all cuts
    for (auto* plot : postFull_) {
      if (printLevel_ > 3)
        std::cout << "        Filling " << plot->getObj()->GetName() << std::endl;

      plot->fill(eventWeight, fullResults);
    }
  }

  delete baseResults;
  delete fullResults;

  if (printLevel_ >= 0) {
    std::cout << "\r      " << iEntry << " events";
    std::cout << std::endl;
  }

  if (printLevel_ > 0) {
    std::cout << "      " << passBase << " passed base selection" << std::endl;
    std::cout << "      " << passFull << " passed full selection" << std::endl;

    for (auto* plots : {&postFull_, &postBase_, &unconditional_}) {
      for (auto* plot : *plots)
        std::cout << "        " << plot->getObj()->GetName() << ": " << plot->getCount() << std::endl;
    }
  }
}
