#! /bin/bash

TreeName=MonoJetTree

if [ "$TreeName" = "" ]
then
    echo ""
    echo " +------------------------------------------------------------+"
    echo " | First argument is the file <TreeName>.                     |"
    echo " | This can be with or without the extension (it's stripped). |"
    echo " | This script then looks for <TreeName>.txt to make a class. |"
    echo " +------------------------------------------------------------+"
    echo ""
    exit
fi

TreeName=${TreeName%%.*}

def=`echo $TreeName | tr "[a-z]" "[A-Z]"`

inVarsFile=$TreeName.txt
h=$TreeName.h
s=$TreeName.cc

echo "#ifndef CROMBIE_"$def"_H" > $h
echo "#define CROMBIE_"$def"_H" >> $h

echo "" >> $h
echo "#include \"TFile.h\"" >> $h
echo "#include \"TTree.h\"" >> $h

declare -a otherTypes=()
for branch in `cat $inVarsFile`
do
    after="${branch##*/}"
    varLetter="${after%=*}"
    if [ "$varLetter" != "F" -a "$varLetter" != "I" -a "$varLetter" != "O" -a "$varLetter" != "VF" -a "$varLetter" != "VI" -a "$varLetter" != "VO" ]; then
        if [ "${varLetter:0:1}" != "V" ]; then
            varType=$varLetter
        else
            varType=${varLetter:1}
        fi
        otherTypes=("${otherTypes[@]}" "$varType")
    fi
done

for objType in `echo "${otherTypes[@]}" | tr ' ' '\n' | sort -u`
do
    echo "#include \""$objType".h\"" >> $h
done

echo "" >> $h
echo "class $TreeName" >> $h
echo "{" >> $h
echo "public:" >> $h
echo "  $TreeName( TTree* tree );" >> $h
echo "  $TreeName( const char* name );" >> $h
echo "  $TreeName( const char* name, TString outFileName );" >> $h
echo "  $TreeName( const char* name, TFile* outFile );" >> $h
echo "  virtual ~$TreeName();" >> $h
echo "" >> $h

for branch in `cat $inVarsFile`
do
    varType=""
    varName="${branch%/*}"
    after="${branch##*/}"
    varLetter="${after%=*}"
    varDefault="${after##*=}"
    if [ "$varLetter" = "F" ]; then
        varType="float"
    elif [ "$varLetter" = "I" ]; then
        varType="int  "
    elif [ "$varLetter" = "O" ]; then
        varType="bool "
    elif [ "$varLetter" = "VF" ]; then
        varType="std::vector<float>*"
    elif [ "$varLetter" = "VI" ]; then
        varType="std::vector<int>*  "
    elif [ "$varLetter" = "VO" ]; then
        varType="std::vector<bool>* "
    elif [ "${varLetter:0:1}" != "V" ]; then
        varType=$varLetter"* "
    else
        varType="std::vector<"${varLetter:1}"*>*"
    fi
    echo "  $varType $varName;" >> $h
done

echo "" >> $h
echo "  TTree*  ReturnTree()                { return t;                             }" >> $h
echo "  void    Fill()                      { t->Fill(); Reset();                   }" >> $h
echo "  void    WriteToFile   ( TFile *f )  { f->WriteTObject(t, t->GetName());     }" >> $h
echo "  void    Write()                     { fFile->WriteTObject(t, t->GetName());"   >> $h
echo "                                        fFile->Close();                       }" >> $h
echo "" >> $h

echo "protected:" >> $h
echo "  TFile* fFile;" >> $h
echo "  TTree* t;" >> $h
echo "  void   Reset();" >> $h
echo "" >> $h
echo "private:" >> $h
echo "  void   SetupTree();" >> $h
echo "" >> $h
echo "  ClassDef($TreeName,1)" >> $h
echo "};" >> $h
echo "#endif" >> $h

echo "#include \"$TreeName.h\"" > $s
echo "" >> $s
echo "ClassImp($TreeName)" >> $s
echo "" >> $s

echo "//--------------------------------------------------------------------------------------------------" >> $s
echo "$TreeName::$TreeName(TTree* tree) :" >> $s
echo "  fFile(0)" >> $s
echo "{" >> $s
echo "  t = tree;" >> $s
echo "  SetupTree();" >> $s
echo "}" >> $s
echo "" >> $s

echo "//--------------------------------------------------------------------------------------------------" >> $s
echo "$TreeName::$TreeName(const char* name) :" >> $s
echo "  fFile(0)" >> $s
echo "{" >> $s
echo "  t = new TTree(name,name);" >> $s
echo "  SetupTree();" >> $s
echo "}" >> $s
echo "" >> $s

echo "//--------------------------------------------------------------------------------------------------" >> $s
echo "$TreeName::$TreeName(const char* name, TString outFileName)" >> $s
echo "{" >> $s
echo "  fFile = new TFile(outFileName,\"RECREATE\");" >> $s
echo "  fFile->cd();" >> $s
echo "  t = new TTree(name,name);" >> $s
echo "  SetupTree();" >> $s
echo "}" >> $s
echo "" >> $s

echo "//--------------------------------------------------------------------------------------------------" >> $s
echo "$TreeName::$TreeName(const char* name, TFile* outFile)" >> $s
echo "{" >> $s
echo "  fFile = outFile;" >> $s
echo "  fFile->cd();" >> $s
echo "  t = new TTree(name,name);" >> $s
echo "  SetupTree();" >> $s
echo "}" >> $s
echo "" >> $s

echo "//--------------------------------------------------------------------------------------------------" >> $s
echo "$TreeName::~$TreeName()" >> $s
echo "{" >> $s
echo "  delete t;" >> $s
echo "  delete fFile;" >> $s
echo "}" >> $s
echo "" >> $s

echo "//--------------------------------------------------------------------------------------------------" >> $s
echo "void" >> $s
echo "$TreeName::Reset()" >> $s
echo "{" >> $s
for branch in `cat $inVarsFile`
do
    varName="${branch%/*}"
    after="${branch##*/}"
    varLetter="${after%=*}"
    varDefault="${after##*=}"
    echo "  $varName = $varDefault;" >> $s
done
echo "}" >> $s
echo "" >> $s


echo "//--------------------------------------------------------------------------------------------------" >> $s
echo "void" >> $s
echo "$TreeName::SetupTree()" >> $s
echo "{" >> $s
for branch in `cat $inVarsFile`
do
    varName="${branch%/*}"
    after="${branch##*/}"
    varLetter="${after%=*}"
    varDefault="${after##*=}"
    if [ "$varLetter" = "I" -o "$varLetter" = "F" -o "$varLetter" = "O" ]; then
        echo "  t->Branch(\"$varName\",&$varName,\"$varName/$varLetter\");" >> $s
    else
        echo "  t->Branch(\"$varName\",&$varName);" >> $s
    fi
done
echo "" >> $s
echo "  Reset();" >> $s
echo "}" >> $s

