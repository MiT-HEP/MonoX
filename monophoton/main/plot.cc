#include "TTree.h"
#include "TFile.h"
#include "TTreeFormula.h"
#include "TH1.h"

#include <stdexcept>
#include <cstring>
#include <iostream>

class ExprFiller {
public:
  ExprFiller() {}
  ExprFiller(char const* name, TTree& tree, char const* expr, char const* cuts, char const* reweight);
  ExprFiller(ExprFiller const&);
  virtual ~ExprFiller();

  TTreeFormula const& getExpr() const { return expr_; }
  void fill(double weight);

  void resetCount() { counter_ = 0; }
  unsigned getCount() const { return counter_; }

protected:
  virtual void doFill_(int) = 0;

  TTreeFormula expr_{};
  TTreeFormula* cuts_{0};
  TTreeFormula* reweight_{0};
  double constReweight_{1.};
  double entryWeight_{1.};
  unsigned counter_{0};
};

class Plot : public ExprFiller {
public:
  Plot() {}
  Plot(TH1& hist, TTree& tree, char const* expr, char const* cuts, char const* reweight);
  Plot(Plot const&);
  ~Plot() {}

private:
  void doFill_(int) override;

  TH1* hist_{0};
};

class Tree : public ExprFiller {
public:
  Tree() {}
  Tree(TTree& outTree, char const* bname, TTree& tree, char const* expr, char const* cuts, char const* reweight);
  Tree(Tree const&);
  ~Tree() {}

private:
  void doFill_(int) override;

  TTree* tree_{0};
  double bvalue_{0.};
};

class Plotter {
public:
  Plotter() {}
  Plotter(char const* path);
  ~Plotter();

  void setBaseSelection(char const* cuts);
  void setFullSelection(char const* cuts);
  void setLuminosity(double l) { lumi_ = l; }
  void setPrescale(unsigned p) { prescale_ = p; }
  void addPlot(TH1* hist, char const* expr, char const* cuts = "", bool applyBaseline = true, bool applyFullSelection = false, char const* reweight = "");
  void addTree(TTree* tree, char const* bname, char const* expr, char const* cuts = "", bool applyBaseline = true, bool applyFullSelection = false, char const* reweight = "");
  void fillPlots();

  void setPrintLevel(int l) { printLevel_ = l; }

private:
  TTree* tree_{0};
  TTreeFormula* baseSelection_{0};
  TTreeFormula* fullSelection_{0};
  double lumi_{1.};
  unsigned prescale_{1};
  std::vector<ExprFiller*> unconditional_{};
  std::vector<ExprFiller*> postBase_{};
  std::vector<ExprFiller*> postFull_{};

  int printLevel_{0};
};

ExprFiller::ExprFiller(char const* name, TTree& tree, char const* expr, char const* cuts, char const* reweight) :
  expr_(name, expr, &tree)
{
  if (cuts && std::strlen(cuts) != 0)
    cuts_ = new TTreeFormula("additionalCuts", cuts, &tree);

  if (reweight && std::strlen(reweight) != 0) {
    reweight_ = new TTreeFormula("reweight", reweight, &tree);
    if (reweight_->GetMultiplicity() == 0) { // this is a constant
      constReweight_ = reweight_->EvalInstance(0);
      delete reweight_;
      reweight_ = 0;
    }
  }
}

ExprFiller::ExprFiller(ExprFiller const& _orig) :
  expr_(_orig.expr_.GetName(), _orig.expr_.GetTitle(), _orig.expr_.GetTree())
{
  if (_orig.cuts_)
    cuts_ = new TTreeFormula("additionalCuts", _orig.cuts_->GetTitle(), _orig.cuts_->GetTree());

  if (_orig.reweight_)
    reweight_ = new TTreeFormula("reweight", _orig.reweight_->GetTitle(), _orig.reweight_->GetTree());

  constReweight_ = _orig.constReweight_;
}

ExprFiller::~ExprFiller()
{
  delete cuts_;
  delete reweight_;
}

void
ExprFiller::fill(double weight)
{
  bool loaded(false);

  for (int iD(0); iD != expr_.GetNdata(); ++iD) {
    if (cuts_ && cuts_->EvalInstance(iD) == 0.)
      continue;

    ++counter_;

    if (!loaded && iD != 0) {
      expr_.EvalInstance(0);
      if (reweight_)
        reweight_->EvalInstance(0);
    }

    entryWeight_ = weight * constReweight_;
    if (reweight_)
      entryWeight_ *= reweight_->EvalInstance(iD);

    doFill_(iD);

    loaded = true;
  }
}


Plot::Plot(TH1& hist, TTree& tree, char const* expr, char const* cuts, char const* reweight) :
  ExprFiller(hist.GetName(), tree, expr, cuts, reweight),
  hist_(&hist)
{
}

Plot::Plot(Plot const& _orig) :
  ExprFiller(_orig),
  hist_(_orig.hist_)
{
}

void
Plot::doFill_(int iD)
{
  hist_->Fill(expr_.EvalInstance(iD), entryWeight_);
}


Tree::Tree(TTree& outTree, char const* bname, TTree& tree, char const* expr, char const* cuts, char const* reweight) :
  ExprFiller(bname, tree, expr, cuts, reweight),
  tree_(&outTree)
{
  tree_->Branch(bname, &bvalue_, TString::Format("%s/D", bname));
  tree_->Branch("weight", &entryWeight_, "weight/D");
}

Tree::Tree(Tree const& _orig) :
  ExprFiller(_orig),
  tree_(_orig.tree_)
{
  tree_->SetBranchAddress(expr_.GetName(), &bvalue_);
  tree_->SetBranchAddress("weight", &entryWeight_);
}

void
Tree::doFill_(int iD)
{
  bvalue_ = expr_.EvalInstance(iD);
  tree_->Fill();
}


Plotter::Plotter(char const* _path)
{
  auto* source(TFile::Open(_path));
  if (!source || source->IsZombie())
    throw std::runtime_error(TString::Format("Cannot open %s", _path).Data());

  tree_ = static_cast<TTree*>(source->Get("events"));
  if (!tree_)
    throw std::runtime_error(TString::Format("Cannot find events tree in %s", _path).Data());    
}

Plotter::~Plotter()
{
  delete baseSelection_;
  delete fullSelection_;

  for (auto* plots : {&postFull_, &postBase_, &unconditional_}) {
    for (auto* plot : *plots)
      delete plot;
  }

  delete tree_->GetCurrentFile();
}

void
Plotter::setBaseSelection(char const* cuts)
{
  if (!cuts || std::strlen(cuts) == 0)
    return;

  delete baseSelection_;

  baseSelection_ = new TTreeFormula("baseSelection", cuts, tree_);
}

void
Plotter::setFullSelection(char const* cuts)
{
  if (!cuts || std::strlen(cuts) == 0)
    return;

  delete fullSelection_;

  fullSelection_ = new TTreeFormula("fullSelection", cuts, tree_);
}

void
Plotter::addPlot(TH1* hist, char const* expr, char const* cuts/* = ""*/, bool applyBaseline/* = true*/, bool applyFullSelection/* = false*/, char const* reweight/* = ""*/)
{
  if (applyBaseline) {
    if (applyFullSelection)
      postFull_.push_back(new Plot(*hist, *tree_, expr, cuts, reweight));
    else
      postBase_.push_back(new Plot(*hist, *tree_, expr, cuts, reweight));
  }
  else
    unconditional_.push_back(new Plot(*hist, *tree_, expr, cuts, reweight));
}

void
Plotter::addTree(TTree* tree, char const* bname, char const* expr, char const* cuts/* = ""*/, bool applyBaseline/* = true*/, bool applyFullSelection/* = false*/, char const* reweight/* = ""*/)
{
  if (applyBaseline) {
    if (applyFullSelection)
      postFull_.push_back(new Tree(*tree, bname, *tree_, expr, cuts, reweight));
    else
      postBase_.push_back(new Tree(*tree, bname, *tree_, expr, cuts, reweight));
  }
  else
    unconditional_.push_back(new Tree(*tree, bname, *tree_, expr, cuts, reweight));
}

void
Plotter::fillPlots()
{
  float weight;
  unsigned eventNumber;

  tree_->SetBranchStatus("*", false);
  tree_->SetBranchStatus("weight", true);
  tree_->SetBranchAddress("weight", &weight);
  if (prescale_ != 1) {
    tree_->SetBranchStatus("eventNumber", true);
    tree_->SetBranchAddress("eventNumber", &eventNumber);
  }

  for (auto* sel : {baseSelection_, fullSelection_}) {
    if (sel) {
      TLeaf* leaf(0);
      int iL(0);
      while ((leaf = sel->GetLeaf(iL++)))
        tree_->SetBranchStatus(leaf->GetBranch()->GetName(), true);
    }
  }

  for (auto* plots : {&postFull_, &postBase_, &unconditional_}) {
    for (auto* plot : *plots) {
      plot->resetCount();

      TLeaf* leaf(0);
      int iL(0);
      while ((leaf = plot->getExpr().GetLeaf(iL++)))
        tree_->SetBranchStatus(leaf->GetBranch()->GetName(), true);
    }
  }

  long iEntry(0);
  unsigned passBase(0);
  unsigned passFull(0);
  while (tree_->GetEntry(iEntry++) > 0) {
    if (printLevel_ >= 0 && iEntry % 10000 == 1)
      std::cout << "\r      " << iEntry;

    if (prescale_ != 1 && eventNumber % prescale_ != 0)
      continue;

    weight *= lumi_;

    for (auto* plot : unconditional_)
      plot->fill(weight);

    if (baseSelection_) {
      int iD(0);
      int nD(baseSelection_->GetNdata());
      for (; iD != nD; ++iD) {
        if (baseSelection_->EvalInstance(iD) != 0.)
          break;
      }
      if (iD == nD)
        continue;
    }

    ++passBase;

    for (auto* plot : postBase_)
      plot->fill(weight);

    if (fullSelection_) {
      int iD(0);
      int nD(fullSelection_->GetNdata());
      for (; iD != nD; ++iD) {
        if (fullSelection_->EvalInstance(iD) != 0.)
          break;
      }
      if (iD == nD)
        continue;
    }

    ++passFull;

    for (auto* plot : postFull_)
      plot->fill(weight);
  }

  if (printLevel_ >= 0) {
    std::cout << "\r      " << iEntry;
    std::cout << std::endl;
  }

  if (printLevel_ > 0) {
    std::cout << "      " << passBase << " passed base selection" << std::endl;
    std::cout << "      " << passFull << " passed full selection" << std::endl;

    for (auto* plots : {&postFull_, &postBase_, &unconditional_}) {
      for (auto* plot : *plots)
        std::cout << "        " << plot->getExpr().GetName() << ": " << plot->getCount() << std::endl;
    }
  }
}
