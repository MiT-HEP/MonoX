#include "Utils/interface/FileMerger.h"

#include "Objects/interface/EventMonophoton.h"

class MPAdd {
public:
  MPAdd() {}
  void addInputPath(char const* path) { merger_.addInput(path); }

  void merge(char const* outPath);

private:
  panda::FileMerger merger_;
};

void
MPAdd::merge(char const* _outPath)
{
  panda::EventMonophoton event;
  merger_.setInEvent(&event);
  merger_.setInputTimeout(300);

  merger_.merge(_outPath);
}
