void
dumpevent(char const* path, unsigned runNumber, unsigned lumiNumber, unsigned eventNumber)
{
  auto* source = TFile::Open(path);
  auto* events = (TTree*)source->Get("events");

  long entry = 0;

  if (runNumber != 0) {
    int n = events->Draw("Entry$", TString::Format("runNumber == %d && lumiNumber == %d && eventNumber == %d", runNumber, lumiNumber, eventNumber), "goff");
    if (n == 0) {
      cout << "Cannot find event " << runNumber << " " << lumiNumber << " " << eventNumber << " in " << path << endl;
      return;
    }

    entry = long(events->GetV1()[0]);
  }

  panda::Event event;
  event.setAddress(*events);
  event.getEntry(*events, entry);

  event.dump();
}
