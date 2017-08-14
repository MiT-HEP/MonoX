void
dumpevent(char const* path, unsigned runNumber, unsigned lumiNumber = 0, unsigned eventNumber = 0)
{
  auto* source = TFile::Open(path);
  auto* events = (TTree*)source->Get("events");

  long entry = 0;

  if (runNumber != 0) {
    if (lumiNumber != 0) {
      int n = events->Draw("Entry$", TString::Format("runNumber == %d && lumiNumber == %d && eventNumber == %d", runNumber, lumiNumber, eventNumber), "goff");
      if (n == 0) {
        cout << "Cannot find event " << runNumber << " " << lumiNumber << " " << eventNumber << " in " << path << endl;
        return;
      }

      entry = long(events->GetV1()[0]);
    }
    else {
      // runNumber is actually the entry number
      entry = runNumber;
    }
  }

  panda::Event event;
  event.setAddress(*events, {"!*", "pfCandidates", "taus", "vertices", "tracks", "superClusters", "electrons", "photons", "muons", "!*.triggerMatch"});
  event.getEntry(*events, entry);

  event.dump();
}
