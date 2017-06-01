#include "TTree.h"
#include "TFile.h"
#include "TTreeFormula.h"
#include "TH1.h"

#include <stdexcept>
#include <cstring>

class Plot {
public:
  Plot() {}
  Plot(TH1& hist, TTree& tree, char const* expr, char const* cuts, char const* reweight, int prescale);
  Plot(Plot const&);
  ~Plot();

  TTreeFormula const& getExpr() const { return expr_; }
  int getPrescale() const { return prescale_; }
  void fill(double weight);

private:
  TH1* hist_{0};
  TTreeFormula expr_{};
  TTreeFormula* cuts_{0};
  TTreeFormula* reweight_{0};
  double constReweight_{1.};
  int prescale_{1};
};

class Plotter {
public:
  Plotter() {}
  Plotter(char const* path);
  ~Plotter();

  void setBaseSelection(char const* cuts);
  void setFullSelection(char const* cuts);
  void addPlot(TH1* hist, char const* expr, char const* cuts = "", char const* reweight = "", bool applyBaseline = true, bool applyFullSelection = false, int prescale = 1);
  void fillPlots();

private:
  TTree* tree_{0};
  TTreeFormula* baseSelection_{0};
  TTreeFormula* fullSelection_{0};
  std::vector<Plot> unconditional_{};
  std::vector<Plot> postBase_{};
  std::vector<Plot> postFull_{};
};

Plot::Plot(TH1& hist, TTree& tree, char const* expr, char const* cuts, char const* reweight, int prescale) :
  hist_(&hist),
  expr_(hist.GetName(), expr, &tree),
  prescale_(prescale)
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

Plot::Plot(Plot const& _orig) :
  hist_(_orig.hist_),
  expr_(_orig.expr_.GetName(), _orig.expr_.GetTitle(), _orig.expr_.GetTree()),
  prescale_(_orig.prescale_)
{
  if (_orig.cuts_)
    cuts_ = new TTreeFormula("additionalCuts", _orig.cuts_->GetTitle(), _orig.cuts_->GetTree());

  if (_orig.reweight_)
    reweight_ = new TTreeFormula("reweight", _orig.reweight_->GetTitle(), _orig.reweight_->GetTree());

  constReweight_ = _orig.constReweight_;
}

Plot::~Plot()
{
  delete cuts_;
  delete reweight_;
}

void
Plot::fill(double weight)
{
  bool loaded(false);

  for (int iD(0); iD != expr_.GetNdata(); ++iD) {
    if (cuts_ && cuts_->EvalInstance64(iD) == 0)
      continue;

    if (!loaded && iD != 0) {
      expr_.EvalInstance(0);
      if (reweight_)
        reweight_->EvalInstance(0);
    }

    double w(weight * constReweight_);
    if (reweight_)
      w *= reweight_->EvalInstance(iD);

    hist_->Fill(expr_.EvalInstance(iD), w);

    loaded = true;
  }
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

  delete tree_->GetCurrentFile();
}

void
Plotter::setBaseSelection(char const* cuts)
{
  if (!cuts || std::strlen(cuts) == 0)
    return;

  baseSelection_ = new TTreeFormula("baseSelection", cuts, tree_);
}

void
Plotter::setFullSelection(char const* cuts)
{
  if (!cuts || std::strlen(cuts) == 0)
    return;

  fullSelection_ = new TTreeFormula("fullSelection", cuts, tree_);
}

void
Plotter::addPlot(TH1* hist, char const* expr, char const* cuts/* = ""*/, char const* reweight/* = ""*/, bool applyBaseline/* = true*/, bool applyFullSelection/* = false*/, int prescale/* = 1*/)
{
  if (applyBaseline) {
    if (applyFullSelection)
      postFull_.emplace_back(*hist, *tree_, expr, cuts, reweight, prescale);
    else
      postBase_.emplace_back(*hist, *tree_, expr, cuts, reweight, prescale);
  }
  else
    unconditional_.emplace_back(*hist, *tree_, expr, cuts, reweight, prescale);
}

void
Plotter::fillPlots()
{
  tree_->SetBranchStatus("*", false);
  tree_->SetBranchStatus("weight", true);
  float weight;
  tree_->SetBranchAddress("weight", &weight);

  for (auto* plots : {&postFull_, &postBase_, &unconditional_}) {
    for (auto& plot : *plots) {
      TLeaf* leaf(0);
      int iL(0);
      while ((leaf = plot.getExpr().GetLeaf(iL++)))
        tree_->SetBranchStatus(leaf->GetBranch()->GetName(), true);
    }
  }

  long iEntry(0);
  while (tree_->GetEntry(iEntry++) > 0) {
    for (auto& plot : unconditional_)
      plot.fill(weight);

    if (baseSelection_) {
      int iD(0);
      int nD(baseSelection_->GetNdata());
      for (; iD != nD; ++iD) {
        if (baseSelection_->EvalInstance64(iD) != 0)
          break;
      }
      if (iD == nD)
        continue;
    }

    for (auto& plot : postBase_)
      plot.fill(weight);

    if (fullSelection_) {
      int iD(0);
      int nD(fullSelection_->GetNdata());
      for (; iD != nD; ++iD) {
        if (fullSelection_->EvalInstance64(iD) != 0)
          break;
      }
      if (iD == nD)
        continue;
    }

    for (auto& plot : postFull_)
      plot.fill(weight);
  }
}
