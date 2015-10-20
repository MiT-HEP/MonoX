#include "TLorentzVector.h"

float deltaPhi(float phi1, float phi2) {
  float PHI = fabs(phi1-phi2);
  if (PHI<=3.14159265)
    return PHI;
  else
    return 2*3.14159265-PHI;
}

float deltaR(float phi1, float eta1, float phi2, float eta2) {
  return sqrt((eta2-eta1)*(eta2-eta1)+deltaPhi(phi1,phi2)*+deltaPhi(phi1,phi2));
}

float uPerp(float met, float metPhi, float zPhi) {
  TLorentzVector recoil;
  recoil.SetPtEtaPhiM(met,0,metPhi + TMath::Pi() - zPhi,0);
  return recoil.Py(); 
}

float uPara(float met, float metPhi, float zPhi) {
  TLorentzVector recoil;
  recoil.SetPtEtaPhiM(met,0,metPhi + TMath::Pi() - zPhi,0);
  return recoil.Px(); 
}

float vectorSumPhi(float pt1, float phi1, float pt2, float phi2){
  TLorentzVector vec1;
  TLorentzVector vec2;
  TLorentzVector vec3;
  vec1.SetPtEtaPhiM(pt1,phi1,0,0);
  vec2.SetPtEtaPhiM(pt2,phi2,0,0);
  vec3 = vec1 + vec2;
  return vec3.Phi();
}

float vectorSumPt(float pt1, float phi1, float pt2, float phi2){
  return sqrt( pow(pt1*cos(phi1) + pt2*cos(phi2),2) +
	       pow(pt1*sin(phi1) + pt2*sin(phi2),2) );
}

float vectorSum3Pt(float pt1, float phi1, float pt2, float phi2,float pt3, float phi3){
  return sqrt( pow(pt1*cos(phi1) + pt2*cos(phi2) + pt3*cos(phi3),2) +
	       pow(pt1*sin(phi1) + pt2*sin(phi2) + pt3*sin(phi3),2) );
}

float vectorSumMass(float pt1, float eta1, float phi1, float pt2, float eta2, float phi2) {
  TLorentzVector vec1;
  TLorentzVector vec2;
  TLorentzVector vec3;
  vec1.SetPtEtaPhiM(pt1,eta1,phi1,0);
  vec2.SetPtEtaPhiM(pt2,eta2,phi2,0);
  vec3 = vec1 + vec2;
  return vec3.M();
}

float vectorSumEta(float pt1, float eta1, float phi1, float pt2, float eta2, float phi2) {
  TLorentzVector vec1;
  TLorentzVector vec2;
  TLorentzVector vec3;
  vec1.SetPtEtaPhiM(pt1,eta1,phi1,0);
  vec2.SetPtEtaPhiM(pt2,eta2,phi2,0);
  vec3 = vec1 + vec2;
  return vec3.Phi();
}

float transverseMass(float lepPt, float lepPhi, float met,  float metPhi) {
  double cosDPhi = cos(deltaPhi(lepPhi,metPhi));
  return sqrt(2*lepPt*met*(1-cosDPhi));
}

