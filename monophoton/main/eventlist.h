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

      list_[run][lumi].insert(event);
    }
  }

  bool inList(panda::Event const& _event) const
  {
    auto rItr(list_.find(_event.runNumber));
    if (rItr == list_.end())
      return false;

    auto lItr(rItr->second.find(_event.lumiNumber));
    if (lItr == rItr->second.end())
      return false;

    auto eItr(lItr->second.find(_event.eventNumber));
    return eItr != lItr->second.end();
  }

 private:
  typedef std::set<unsigned> EventContainer;
  typedef std::map<unsigned, EventContainer> LumiContainer;
  typedef std::map<unsigned, LumiContainer> RunContainer;

  RunContainer list_{};
};
