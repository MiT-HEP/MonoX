#include <fstream>
#include <string>
#include <map>
#include <set>

class EventList {
 public:
  EventList() {}
  EventList(char const* _path)
  {
    addSource(_path);
  }

  void addSource(char const* _path)
  {
    std::ifstream input(_path);
    std::string line;

    while (true) {
      std::getline(input, line);
      if (!input.good())
        break;

      unsigned run(std::atoi(line.substr(0, line.find(":")).c_str()));
      unsigned lumi(std::atoi(line.substr(line.find(":") + 1, line.rfind(":")).c_str()));
      unsigned event(std::atoi(line.substr(line.rfind(":") + 1).c_str()));

      // printf("%u:%u:%u \n", run, lumi, event);

      list_[run][lumi].insert(event);
    }

    rEnd_ = list_.end();
  }

  bool inList(simpletree::Event const& _event) const
  {
    // printf("run: %u \n", _event.run);
    // printf("rcount: %lu \n", list_.count(_event.run));
    if ( list_.count(_event.run) == 0)
      return false;
    // auto rItr(list_.find(_event.run));
    // // printf("rItr: %u \n", rItr->first);
    // if (rItr == rEnd_)
    // return false;

    // printf("lumi: %u \n", _event.lumi);
    // printf("lcount: %lu \n", list_.at(_event.run).count(_event.lumi));
    if ( list_.at(_event.run).count(_event.lumi) == 0)
      return false;
    // auto lItr(rItr->second.find(_event.lumi));
    // printf("lItr: %u \n", lItr->first);
    // if (lItr == rItr->second.end())
    // return false;

    // printf("event: %u \n", _event.event);
    // printf("ecount: %lu \n", list_.at(_event.run).at(_event.lumi).count(_event.event));
    if ( list_.at(_event.run).at(_event.lumi).count(_event.event) == 0)
      return false;
    // auto eItr(lItr->second.find(_event.event));
    // printf("eItr: %u \n", *eItr);
    // return eItr != lItr->second.end();

    return true;
  }

 private:
  typedef std::set<unsigned> EventContainer;
  typedef std::map<unsigned, EventContainer> LumiContainer;
  typedef std::map<unsigned, LumiContainer> RunContainer;
  RunContainer list_{};
  RunContainer::const_iterator rEnd_{};
  // std::map<unsigned, std::map<unsigned, std::set<unsigned>>> list_{};
  // std::map<unsigned, std::map<unsigned, std::set<unsigned>>>::const_iterator rEnd_{};
};
