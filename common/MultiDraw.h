#ifndef PLOT_H
#define PLOT_H

#include "TChain.h"
#include "TTreeFormula.h"
#include "TH1.h"
#include "TString.h"

#include <map>
#include <vector>

//! Cached version of TTreeFormula.
/*!
 * Buys little speedup though. The main reason for implementing such a class is to have the
 * number of leaves exposed - TTreeFormula only provides GetLeaf(Int_t) which calls
 * fLeaves.UncheckedAt(), and at least in one instance it returned an invalid pointer.
 */
class TTreeFormulaCached : public TTreeFormula {
public:
  TTreeFormulaCached(char const* name, char const* formula, TTree* tree) : TTreeFormula(name, formula, tree) {}
  ~TTreeFormulaCached() {}

  Int_t GetNdata() override;
  Double_t EvalInstance(Int_t, char const* [] = 0) override;

  TObjArray const* GetLeaves() const { return &fLeaves; }

private:
  std::vector<std::pair<Bool_t, Double_t>> fCache{};
};

//! Filler object base class with expressions, a cut, and a reweight.
/*!
 * Inherited by Plot (histogram) and Tree (tree). Does not own any of
 * the TTreeFormula objects by default.
 */
class ExprFiller {
public:
  ExprFiller() {}
  ExprFiller(TTreeFormula* cuts, TTreeFormula* reweight);
  ExprFiller(ExprFiller const&);
  virtual ~ExprFiller();

  void addExpr(TTreeFormula* expr) { exprs_.push_back(expr); }
  void ownFormulas(bool b) { ownFormulas_ = b; }

  unsigned getNdim() const { return exprs_.size(); }
  TTreeFormula const* getExpr(unsigned iE = 0) const { return exprs_.at(iE); }
  TTreeFormula* getExpr(unsigned iE = 0) { return exprs_.at(iE); }
  TTreeFormula const* getCuts() const { return cuts_; }
  TTreeFormula* getCuts() { return cuts_; }
  TTreeFormula const* getReweight() const { return reweight_; }
  void updateTree();
  void fill(double weight, std::vector<bool> const* = 0);

  virtual TObject const* getObj() const = 0;

  void resetCount() { counter_ = 0; }
  unsigned getCount() const { return counter_; }

protected:
  virtual void doFill_(unsigned) = 0;

  std::vector<TTreeFormula*> exprs_{};
  TTreeFormula* cuts_{0};
  TTreeFormula* reweight_{0};
  bool ownFormulas_{false};
  double entryWeight_{1.};
  unsigned counter_{0};
};

class Plot : public ExprFiller {
public:
  Plot() {}
  Plot(TH1& hist, TTreeFormula* expr, TTreeFormula* cuts, TTreeFormula* reweight);
  Plot(Plot const&);
  ~Plot() {}

  TObject const* getObj() const override { return hist_; }
  TH1 const* getHist() const { return hist_; }

private:
  void doFill_(unsigned) override;

  TH1* hist_{0};
};

class Tree : public ExprFiller {
public:
  Tree() {}
  Tree(TTree& outTree, TTreeFormula* cuts, TTreeFormula* reweight);
  Tree(Tree const&);
  ~Tree() {}

  void addBranch(char const* bname, TTreeFormula* expr);

  TObject const* getObj() const override { return tree_; }
  TTree const* getTree() const { return tree_; }

  static unsigned const NBRANCHMAX = 128;

private:
  void doFill_(unsigned) override;

  TTree* tree_{0};
  std::vector<double> bvalues_{};
};

class MultiDraw {
public:
  MultiDraw(char const* path = "");
  ~MultiDraw();

  void addInputPath(char const* path) { tree_.Add(path); }
  void setWeightBranch(char const* bname) { weightBranchName_ = bname; }
  void setBaseSelection(char const* cuts);
  void setFullSelection(char const* cuts);
  void setLuminosity(double l) { lumi_ = l; }
  void setPrescale(unsigned p) { prescale_ = p; }
  void addPlot(TH1* hist, char const* expr, char const* cuts = "", bool applyBaseline = true, bool applyFullSelection = false, char const* reweight = "");
  void addTree(TTree* tree, char const* cuts = "", bool applyBaseline = true, bool applyFullSelection = false, char const* reweight = "");
  void addTreeBranch(TTree* tree, char const* bname, char const* expr);
  void fillPlots(long nEntries = -1);

  void setPrintLevel(int l) { printLevel_ = l; }

private:
  //! Handle addPlot and addTree with the same interface (requires a callback to generate the right object)
  typedef std::function<ExprFiller*(TTreeFormula*, TTreeFormula*)> ObjGen;
  void addObj_(char const* cuts, bool applyBaseline, bool applyFullSelection, char const* reweight, ObjGen const&);

  TTreeFormulaCached* getFormula_(char const*);

  TChain tree_;
  TString weightBranchName_;
  TTreeFormula* baseSelection_{0};
  TTreeFormula* fullSelection_{0};
  double lumi_{1.};
  unsigned prescale_{1};
  std::vector<ExprFiller*> unconditional_{};
  std::vector<ExprFiller*> postBase_{};
  std::vector<ExprFiller*> postFull_{};

  std::map<TString, TTreeFormulaCached*> library_;

  int printLevel_{0};
};

#endif
