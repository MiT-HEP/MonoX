#! /bin/bash

package=Merged

outFileBase=$package\Tree
def=`echo $package | tr "[a-z]" "[A-Z]"`

inVarsFile=$outFileBase.txt
h=$outFileBase.h
s=$outFileBase.cc

echo "#ifndef MITCROMBIE_"$def"_"$def"TREE_H" > $h
echo "#define MITCROMBIE_"$def"_"$def"TREE_H" >> $h

echo "" >> $h
echo "#include \"TFile.h\"" >> $h
echo "#include \"TTree.h\"" >> $h

declare -a otherTypes=()
for branch in `cat $inVarsFile`; do
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

for objType in `echo "${otherTypes[@]}" | tr ' ' '\n' | sort -u`; do
    echo "#include \""$objType".h\"" >> $h
done

echo "" >> $h
echo "class $outFileBase" >> $h
echo "{" >> $h
echo "public:" >> $h
echo "  $outFileBase( const char *name );" >> $h
echo "  virtual ~$outFileBase();" >> $h
echo "" >> $h

for branch in `cat $inVarsFile`; do
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
echo "  TTree  *ReturnTree()                { return t;                            }" >> $h
echo "  void    Fill()                      { t->Fill(); Reset();                  }" >> $h
echo "  void    WriteToFile( TFile *file )  { file->WriteTObject(t, t->GetName()); }" >> $h
echo "" >> $h

echo "protected:" >> $h
echo "" >> $h
echo "  TTree *t;" >> $h
echo "  void   Reset();" >> $h
echo "" >> $h
echo "  ClassDef($outFileBase,1)" >> $h
echo "};" >> $h
echo "#endif" >> $h

echo "#include \"$outFileBase.h\"" > $s
echo "" >> $s
echo "ClassImp($outFileBase)" >> $s
echo "" >> $s

echo "//--------------------------------------------------------------------------------------------------" >> $s
echo "$outFileBase::$outFileBase(const char *name)" >> $s
echo "{ " >> $s
echo "  t = new TTree(name,name);" >> $s
echo "" >> $s
for branch in `cat $inVarsFile`; do
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
echo "" >> $s

echo "//--------------------------------------------------------------------------------------------------" >> $s
echo "$outFileBase::~$outFileBase()" >> $s
echo "{" >> $s
echo "  delete t;" >> $s
echo "}" >> $s
echo "" >> $s

echo "//--------------------------------------------------------------------------------------------------" >> $s
echo "void" >> $s
echo "$outFileBase::Reset()" >> $s
echo "{" >> $s
for branch in `cat $inVarsFile`; do
    varName="${branch%/*}"
    after="${branch##*/}"
    varLetter="${after%=*}"
    varDefault="${after##*=}"
    echo "  $varName = $varDefault;" >> $s
done
echo "}" >> $s
