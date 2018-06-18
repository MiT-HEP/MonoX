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
 *
 * User of this class must first call ResetCache() and GetNdata() in the order to properly
 * access the instance value. Value of fNdataCache is returned for the second and subsequent
 * calls to GetNdata(). Instances are evaluated and cached at the first call of EvalInstance()
 * for the respective indices.
 */
class TTreeFormulaCached : public TTreeFormula {
public:
  TTreeFormulaCached(char const* name, char const* formula, TTree* tree) : TTreeFormula(name, formula, tree) {}
  ~TTreeFormulaCached() {}

  Int_t GetNdata() override;
  Double_t EvalInstance(Int_t, char const* [] = nullptr) override;

  void ResetCache() { fNdataCache = -1; }
  TObjArray const* GetLeaves() const { return &fLeaves; }
  void SetNRef(UInt_t n) { fNRef = n; }
  UInt_t GetNRef() const { return fNRef; }

private:
  Int_t fNdataCache{-1};
  UInt_t fNRef{1};
  std::vector<std::pair<Bool_t, Double_t>> fCache{};
};

//! Filler object base class with expressions, a cut, and a reweight.
/*!
 * Inherited by Plot (histogram) and Tree (tree). Does not own any of
 * the TTreeFormula objects by default.
 */
class ExprFiller {
public:
  ExprFiller(TTreeFormula* cuts = nullptr, TTreeFormula* reweight = nullptr);
  ExprFiller(ExprFiller const&);
  virtual ~ExprFiller();

  void ownFormulas(bool b) { ownFormulas_ = b; }

  unsigned getNdim() const { return exprs_.size(); }
  TTreeFormula const* getExpr(unsigned iE = 0) const { return exprs_.at(iE); }
  TTreeFormula* getExpr(unsigned iE = 0) { return exprs_.at(iE); }
  TTreeFormula const* getCuts() const { return cuts_; }
  TTreeFormula* getCuts() { return cuts_; }
  TTreeFormula const* getReweight() const { return reweight_; }
  void updateTree();
  void fill(std::vector<double> const& eventWeights, std::vector<bool> const* = nullptr);

  virtual TObject const* getObj() const = 0;

  void resetCount() { counter_ = 0; }
  unsigned getCount() const { return counter_; }

  void setPrintLevel(int l) { printLevel_ = l; }

protected:
  virtual void doFill_(unsigned) = 0;

  std::vector<TTreeFormula*> exprs_{};
  TTreeFormula* cuts_{nullptr};
  TTreeFormula* reweight_{nullptr};
  bool ownFormulas_{false};
  double entryWeight_{1.};
  unsigned counter_{0};

  int printLevel_{0};
};

//! A wrapper class for TH1
/*!
 * The class is to be used within MultiDraw, and is instantiated by addPlot().
 * Arguments:
 *  TH1& hist               The actual histogram object (user is responsible to create it)
 *  TTreeFormula& expr      Expression whose evaluated value gets filled to the plot
 *  TTreeFormula* cuts      If provided and evaluates to 0, the plot is not filled
 *  TTreeFormula* reweight  If provided, evalutaed and used as weight for filling the histogram
 *  double overflowBinSize  If 0, overflow is not handled explicitly (i.e. TH1 fills the n+1-st bin)
 *                          If >0, an overflow bin with size (original width)*overflowBinSize is created
 *                          If <0, the ove
 */
class Plot : public ExprFiller {
public:
  enum OverflowMode {
    kNoOverflowBin,
    kDedicated,
    kMergeLast
  };

  Plot() {}
  Plot(TH1& hist, TTreeFormula& expr, TTreeFormula* cuts = nullptr, TTreeFormula* reweight = nullptr, OverflowMode mode = kNoOverflowBin);
  Plot(Plot const&);
  ~Plot() {}

  TObject const* getObj() const override { return hist_; }
  TH1 const* getHist() const { return hist_; }

private:
  void doFill_(unsigned) override;

  TH1* hist_{nullptr};
  OverflowMode overflowMode_{kNoOverflowBin};
};

class Tree : public ExprFiller {
public:
  Tree() {}
  Tree(TTree& tree, TTreeFormula* cuts = nullptr, TTreeFormula* reweight = nullptr);
  Tree(Tree const&);
  ~Tree() {}

  void addBranch(char const* bname, TTreeFormula& expr);

  TObject const* getObj() const override { return tree_; }
  TTree const* getTree() const { return tree_; }

  static unsigned const NBRANCHMAX = 128;

private:
  void doFill_(unsigned) override;

  TTree* tree_{nullptr};
  std::vector<double> bvalues_{};
};

//! A handy class to fill multiple histograms in one pass over a TChain using string expressions.
/*!
 * Usage
 *  MultiDraw drawer;
 *  drawer.addInputPath("source.root");
 *  drawer.setBaseSelection("electrons.loose && TMath::Abs(electrons.eta_) < 1.5");
 *  drawer.setFullSelection("electrons.tight");
 *  TH1D* h1 = new TH1D("h1", "histogram 1", 100, 0., 100.);
 *  TH1D* h2 = new TH1D("h2", "histogram 2", 100, 0., 100.);
 *  drawer.addPlot(h1, "electrons.pt_", "", true, false);
 *  drawer.addPlot(h2, "electrons.pt_", "", true, true);
 *  drawer.fillPlots();
 *
 * In the above example, histogram h1 is filled with the pt of the loose barrel electrons, and
 * h2 with the subset of such electrons that also pass the tight selection.
 * It is also possible to set cuts and reweights for individual plots. Event-wide weights can
 * be set by three methods setWeightBranch, setConstantWeight, and setGlobalReweight.
 */
class MultiDraw {
public:
  //! Constructor.
  /*!
   * \param treeName  Name of the input tree.
   */
  MultiDraw(char const* treeName = "events");
  ~MultiDraw();

  //! Add an input file.
  void addInputPath(char const* path) { tree_.Add(path); }
  //! Set the name and the C variable type of the weight branch. Pass an empty string to unset.
  void setWeightBranch(char const* bname, char type = 'F') { weightBranchName_ = bname; }
  //! Set the baseline selection.
  void setBaseSelection(char const* cuts);
  //! Set the full selection.
  void setFullSelection(char const* cuts);
  //! Apply a constant weight (e.g. luminosity times cross section) to all events.
  void setConstantWeight(double l) { constWeight_ = l; }
  //! Set a prescale factor
  /*!
   * When prescale_ > 1, only events that satisfy eventNumber % prescale_ == 0 are read.
   */
  void setPrescale(unsigned p) { prescale_ = p; }
  //! Set a global reweight
  /*!
   * Reweight factor can be set in two ways. If the second argument is nullptr,
   * the value of expr in every event is used as the weight. If instead a TH1,
   * TGraph, or TF1 is passed as the second argument, the value of expr is used
   * to look up the y value of the source object, which is used as the weight.
   */
  void setReweight(char const* expr, TObject const* source = nullptr);
  //! Add a histogram to fill.
  /*!
   * Currently only 1D histograms can be used.
   */
  void addPlot(TH1* hist, char const* expr, char const* cuts = "", bool applyBaseline = true, bool applyFullSelection = false, char const* reweight = "", Plot::OverflowMode mode = Plot::kNoOverflowBin);
  //! Add a tree to fill.
  /*!
   * Use addTreeBranch to add branches.
   */
  void addTree(TTree* tree, char const* cuts = "", bool applyBaseline = true, bool applyFullSelection = false, char const* reweight = "");
  //! Add a branch to a tree already added to the MultiDraw object.
  void addTreeBranch(TTree* tree, char const* bname, char const* expr);

  //! Run and fill the plots and trees.
  void fillPlots(long nEntries = -1, long firstEntry = 0);

  void setPrintLevel(int l) { printLevel_ = l; }
  long getTotalEvents() { return totalEvents_; }

  unsigned numObjs() const { return unconditional_.size() + postBase_.size() + postFull_.size(); }

private:
  //! Handle addPlot and addTree with the same interface (requires a callback to generate the right object)
  typedef std::function<ExprFiller*(TTreeFormula*, TTreeFormula*)> ObjGen;
  void addObj_(char const* cuts, bool applyBaseline, bool applyFullSelection, char const* reweight, ObjGen const&);

  TTreeFormulaCached* getFormula_(char const*);
  void deleteFormula_(TTreeFormulaCached*);

  TChain tree_;
  TString weightBranchName_{"weight"};
  TTreeFormulaCached* baseSelection_{nullptr};
  TTreeFormulaCached* fullSelection_{nullptr};
  double constWeight_{1.};
  unsigned prescale_{1};
  TTreeFormulaCached* reweightExpr_{nullptr};
  std::function<void(std::vector<double>&)> reweight_;
  std::vector<ExprFiller*> unconditional_{};
  std::vector<ExprFiller*> postBase_{};
  std::vector<ExprFiller*> postFull_{};

  std::map<TString, TTreeFormulaCached*> library_;

  int printLevel_{0};
  long totalEvents_{0};
};

#endif
