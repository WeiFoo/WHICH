#include "Data.h"
#include "Rule.h"
#include "defines.h"
#include <iostream>
#include <algorithm>
#include <cmath>
#include <sstream>
using namespace std;

Data::Data() {}

Data::~Data() 
{
	while ( mInstances.size() > 0  )
	{
		vector< InstanceElement * > *i = mInstances.back();
		while ( i->size() > 0 )
		{
			InstanceElement *ie = i->back();
			i->pop_back();
			delete ie;
		}
		mInstances.pop_back();
		delete i;
	}

	while ( mAttrValFreqs.size() > 0 )
	{
		vector< int * > tmpV = mAttrValFreqs.back();
		while ( tmpV.size() > 0 )
		{
			int *tmp = tmpV.back();
			tmpV.pop_back();
			delete tmp;
		}
		mAttrValFreqs.pop_back();
	}
}

void Data::read( string fName )
{
	ifstream file( fName.c_str() );
	mFileName = fName;
//	if ( !file.is_open() )
//	{
//		cerr << "Error opening file " << fName << ". Exiting." << endl;
//		exit( 0 );
//	}

	string line;
	bool atData = false;
	int index;
	while ( !file.eof() )
	{
		getline( file, line, '\n' );
		for ( unsigned int i = 0; i < line.length(); i++ )
			if ( line[i] >= 'A' && line[i] <= 'Z' ) line[i] = line[i] - 'A' + 'a';

		// Skip blank lines
		if ( line.empty() || line.find( "@relation" ) != string::npos || line.find( "%" ) != string::npos ) continue;
		
		if ( line.find( "@data" ) != string::npos )
		{
			mClassName = mAtts[ mAtts.size()-1 ];
			mClassFreqs.resize( mAttVals[mClassName].size() );
			for ( unsigned int i = 0; i < mClassFreqs.size(); i++ ) mClassFreqs[i] = 0;
			atData = true;
			continue;
		}

		if ( !atData ) processAttribute( preprocessString( line ) );
		else processInstance( preprocessString( line ) );
	}
}

void Data::discretizeEqInt( int bins, Data *combine )
{
  vector< vector< InstanceElement * > * > allData;
  
  if ( combine == NULL ) 
  {
		allData.resize( mInstances.size() );
		for ( unsigned int i = 0; i < mInstances.size(); i++ )
		{
			allData[i] = new vector< InstanceElement * >( mInstances[i]->size() );
			for ( unsigned int j = 0; j < mInstances[i]->size(); j++ )
			{
				allData[i]->at(j) = new InstanceElement();
				if ( mIsReal[j] ) allData[i]->at(j)->mValue = mInstances[i]->at( j )->mValue;
				else allData[i]->at(j)->mIndex = mInstances[i]->at( j )->mIndex;
			}
		}
  }
  else
  {
    for ( unsigned int i = 0; i < mInstances.size(); i++ )
    {
	   allData.push_back( new vector< InstanceElement * >() );
	   for ( unsigned int j = 0; j < mInstances[i]->size(); j++ )
	   {
		   allData.back()->push_back( new InstanceElement() );
		   //allData.back()->at( j )->mIsUnknown = false;
		   //if ( mInstances[i]->at( j )->mIsUnknown ) allData.back()->at( j )->mIsUnknown = true;
		   /*else*/ if ( mIsReal[j] ) allData.back()->at( j )->mValue = mInstances[i]->at( j )->mValue;
		   else allData.back()->at( j )->mIndex = mInstances[i]->at( j )->mIndex;
	  }
	}

    for ( unsigned int i = 0; i < combine->mInstances.size(); i++ )
    {
		allData.push_back( new vector< InstanceElement * >() );
		for ( unsigned int j = 0; j < combine->mInstances[i]->size(); j++ )
		{
			allData.back()->push_back( new InstanceElement() );
			//allData.back()->at( j )->mIsUnknown = false;
			//if ( combine->mInstances[i]->at( j )->mIsUnknown ) allData.back()->at( j )->mIsUnknown = true;
			/*else*/ if ( combine->mIsReal[j] ) allData.back()->at( j )->mValue = combine->mInstances[i]->at( j )->mValue;
			else allData.back()->at( j )->mIndex = combine->mInstances[i]->at( j )->mIndex;
		}
	}
  }

  for ( unsigned int att = 0; att < mAtts.size(); att++ )
  {
    if ( mIsReal[att] )
    {
      mAttVals[mAtts[att]].resize(bins);
	  if ( combine != NULL )
		combine->mAttVals[mAtts[att]].resize(bins);


	  if ( allData[0]->at(att)->mValue < 0.0001 ) allData[0]->at(att)->mValue = 0.0001;
	  allData[0]->at(att)->mValue = log10( allData[0]->at(att)->mValue );
	  //allData[0]->at(att)->mValue = allData[0]->at(att)->mValue;
      float minima = allData[0]->at(att)->mValue, maxima = minima;
      for ( unsigned int item = 1; item < allData.size(); item++ )
      {
	    if ( allData[item]->at(att)->mValue < 0.0001 ) allData[item]->at(att)->mValue = 0.0001;
	    allData[item]->at(att)->mValue = log10( allData[item]->at(att)->mValue );
		//allData[item]->at(att)->mValue = allData[item]->at(att)->mValue;
		minima = min( minima, allData[item]->at(att)->mValue );
		maxima = max( maxima, allData[item]->at(att)->mValue );
      }
	  int binCnts[10] = {0,0,0,0,0,0,0,0,0,0};
      for ( unsigned int item = 1; item < allData.size(); item++ )
	  {
		  int binNo = (allData[item]->at(att)->mValue-minima)/(maxima-minima)*bins;
		  binCnts[binNo]++;
		  if ( item < mInstances.size() )
			  mInstances[item]->at(att)->mIndex = binNo;
		  else
			  combine->mInstances[item-mInstances.size()]->at(att)->mIndex = binNo;
      }

	  for ( int b = 0; b < 10; b++ )
		cout << "Bin " << b+1 << ": " << binCnts[b]/(float)allData.size()*100 << endl;
	  cout << endl;

	  float incr = (maxima-minima)/(float)bins;
	  for ( unsigned int b = 0; b < bins; b++ )
	  {
		  stringstream ss( stringstream::in | stringstream::out );
		  //ss << "[ " << pow(10,b*incr+minima) << " to " << pow(10, (b+1)*incr+minima) << " ]" << endl;
		  ss << "[ " << b*incr+minima << " to " << (b+1)*incr+minima << " ]" << endl;
		  getline( ss, mAttVals[mAtts[att]][b] );
		  if ( combine != NULL )
			combine->mAttVals[mAtts[att]][b] = mAttVals[mAtts[att]][b];
	  }

      mIsReal[att] = false;
	  if ( combine != NULL ) combine->mIsReal[att] = false;
    }
  }  
}

void Data::discretizeEqFreq( int bins, Data *combine ) // the original algorithm is Equal Width Disrectizetion
{
	vector< vector < InstanceElement * > * > allData;

	if ( combine == NULL ) 
	{
		allData.resize( mInstances.size() );
		for ( unsigned int i = 0; i < mInstances.size(); i++ )
		{
			allData[i] = new vector< InstanceElement * >( mInstances[i]->size() );
			for ( unsigned int j = 0; j < mInstances[i]->size(); j++ )
			{
				allData[i]->at(j) = new InstanceElement();
				if ( mIsReal[j] ) allData[i]->at(j)->mValue = mInstances[i]->at( j )->mValue;
				else allData[i]->at(j)->mIndex = mInstances[i]->at( j )->mIndex;
			}
		}
	}
	else
	{
		for ( unsigned int i = 0; i < mInstances.size(); i++ )
		{
			allData.push_back( new vector< InstanceElement * >() );
			for ( unsigned int j = 0; j < mInstances[i]->size(); j++ )
			{
				allData.back()->push_back( new InstanceElement() );
				if ( mIsReal[j] ) allData.back()->at( j )->mValue = mInstances[i]->at( j )->mValue;
				else allData.back()->at( j )->mIndex = mInstances[i]->at( j )->mIndex;
			}
		}

		for ( unsigned int i = 0; i < combine->mInstances.size(); i++ )
		{
			allData.push_back( new vector< InstanceElement * >() );
			for ( unsigned int j = 0; j < combine->mInstances[i]->size(); j++ )
			{
				allData.back()->push_back( new InstanceElement() );
				if ( combine->mIsReal[j] ) allData.back()->at( j )->mValue = combine->mInstances[i]->at( j )->mValue;
				else allData.back()->at( j )->mIndex = combine->mInstances[i]->at( j )->mIndex;
			}
		}
	}


	for ( unsigned int att = 0; att < mAtts.size(); att++ )
	{
		if ( mIsReal[att] )
		{
			// Get a vector of all the values this continuous attribute has.
			vector< ListItem > mItems( allData.size() );
			float *mins = new float[bins], *maxes = new float[bins];
			
			for ( int b = 0; b < bins; b++ )
			{
				mins[b] = pow(10, 5);
				maxes[b] = pow(-10, 5);
			}

			for ( unsigned int i = 0; i < allData.size(); i++ )
			{
				//if ( allData[i]->at( att )->mValue < 0.00001 ) allData[i]->at( att )->mValue = 0.00001;
				mItems[i].mPos = i;
				//mItems[i].mVal = log10( allData[i]->at( att )->mValue );
				mItems[i].mVal = allData[i]->at( att )->mValue;
			}

			sort( mItems.begin(), mItems.end() );

			// Change this attribute to discrete.
			mAttVals[mAtts[att]].resize( bins );
			if ( combine != NULL )
				combine->mAttVals[combine->mAtts[att]].resize( bins );
//            // from here by Foo
//            int distance = (int) mItems.size()/bins;
//            int *cut = new int[bins];
//            for (unsigned int i = 0; i < bins; i++) {
//                if (i + distance < mItems.size())
//                {
//                    cut[i] = i + distance;
//                }
//                else
//                {
//                    cut[i] = mItems.size();
//                }
//            }
//            for (unsigned int i = 0; i < mItems.size();i++)
//            {
//                int binNo = floor(i/(float)mItems.size() * bins);
//                unsigned int pos = mItems[i].mPos;
//                if(pos <= *cut)
//                {
//                    mins[binNo] = min(mins[binNo], mItems[i].mVal);
//                    
//                }
//                
//            }
			
			for ( unsigned int i = 0; i < mItems.size(); i++ )
			{
				int binNo = floor(i/(float)mItems.size() * bins);
				unsigned int pos = mItems[i].mPos;

				mins[binNo] = min( mins[binNo], mItems[i].mVal );
				maxes[binNo] = max( mins[binNo], mItems[i].mVal );
				if ( pos < mInstances.size() ) mInstances[pos]->at( att )->mIndex = binNo;
				else combine->mInstances[pos - mInstances.size()]->at( att )->mIndex = binNo;
			}
			
			mIsReal[att] = false;
			if ( combine != NULL ) combine->mIsReal[att] = false;

			// Change the AttVal vector for this attribute to bin number of elements that
			// best describe this attribute's bins.
			for ( unsigned int b = 0; b < bins; b++ )
			{
				stringstream ss( stringstream::in | stringstream::out );
				//ss << "[ " << pow(10, (mins[b])) << " to " << pow(10, (maxes[b])) << " ]" << endl;
				ss << "[ " << (mins[b]) << " to " << (maxes[b]) << " ]" << endl;
				getline( ss, mAttVals[mAtts[att]][b] );
				if ( combine != NULL )
					combine->mAttVals[combine->mAtts[att]][b] = mAttVals[mAtts[att]][b];
			}
			
			delete mins;
			delete maxes;
		}
	}

	while ( allData.size() > 0 )
	{
		vector< InstanceElement * > *b = allData.back();
		allData.pop_back();
		while ( b->size() > 0 )
		{
			InstanceElement *ie = b->back();
			b->pop_back();
			delete ie;
		}
		delete b;
	}
}

bool Data::subsample( unsigned int desClass, float per )
{
	// If the desiered class index is not within the bounds of the
	// number of class values, error and exit.
	if ( desClass < 0 || desClass >= mClassFreqs.size() )
	{
		cerr << desClass << " out of range, exiting." << endl;
		exit( 1 );
	}

	// Check to make sure percentage is a valid percentage.
	if ( per < 0 || per > 1 )
	{
		cerr << per << " is not a valid percentage( 0-1 ), exiting." << endl;
		exit( 1 );
	}

	float natPer;
	int desSum, toRemove;

	// Calculate the natural percentage.
	natPer = mClassFreqs[desClass]/(float)mInstances.size();

	// If the natural percentage is greater than or equal to the
	// desired percentage, return false.
	if ( natPer >= per ) return false;

	desSum = floor( (natPer*mInstances.size())/per ); 
	toRemove = mInstances.size() - desSum;
	if ( toRemove < 0 ) toRemove = 0;

	// Remove toRemove amount of non desired classes from set.
	for ( unsigned int i = 0; i < toRemove; i++ )
	{
		int inst = 0, cnt = 0;
		vector< vector< InstanceElement * > * >::iterator instItr; 
		InstanceElement *ie;
		do
		{
			inst = randomNum( 0,mInstances.size()-1 );
		} while ( getClassIndex( mInstances[inst] ) == desClass );
		instItr = mInstances.begin();
		while ( cnt++ < inst && instItr++ != mInstances.begin() );
		while ( (*instItr)->size() > 0 )
		{
			ie = (*instItr)->back();
			(*instItr)->pop_back();
			delete ie;
		}
		mInstances.erase( instItr );
		delete (*instItr );
	}

	// Recalculate the class frequencies.
	for ( unsigned int i = 0; i < mClassFreqs.size(); i++ ) mClassFreqs[i] = 0;
	for ( unsigned int i = 0; i < mInstances.size(); i++ )
		mClassFreqs[getClassIndex( mInstances[i] )]++;

	return true;
}

unsigned int Data::microsample( unsigned int amount )
{
  for ( unsigned int c = 0; c < mClassFreqs.size(); c++ )
    if ( mClassFreqs[c] < amount ) amount = mClassFreqs[c];

  for ( unsigned int c = 0; c < mClassFreqs.size(); c++ )
  {
    unsigned int toRemove = mClassFreqs[c] - amount;
    for ( unsigned int r = 0; r < toRemove; r++ )
    {
      unsigned int inst = randomNum( 0, mInstances.size() - 1 );
      vector< vector< InstanceElement * > *>::iterator instItr = mInstances.begin();
      while ( getClassIndex( mInstances[inst] ) != c )
      {
	inst = randomNum( 0, mInstances.size() - 1 );
      }
      for ( unsigned int i = 0; i < inst; i++ ) instItr++;
      while ( (*instItr)->size() > 0 )
      {
	InstanceElement *ie = (*instItr)->back();
	(*instItr)->pop_back();
	delete ie;
      }
      vector< InstanceElement *> *t = *instItr;
      mInstances.erase( instItr );
      delete  t;
    }
  }

  for ( unsigned int c = 0; c < mClassFreqs.size(); c++ )
    mClassFreqs[c] = amount;

  return amount;
}

void Data::normalizeAttribute( int attIndex )
{
  float tot = 0;
  if ( attIndex < 0 || attIndex > mAtts.size() )
  {
    cerr << "Can not normalize. Attribute index " << attIndex << " is out of range. Exiting." << endl;
    exit( 1 );
  }
  else if ( !mIsReal[attIndex] )
  {
    cerr << "Can not normalize. Attribute " << mAtts[attIndex] << " is not real. Exiting." << endl;
    exit( 1 );
  }

  for ( unsigned int item = 0; item < mInstances.size(); item++ )
  {
    tot += mInstances[item]->at(attIndex)->mValue;
  }
  
  for ( unsigned int item = 0; item < mInstances.size(); item++ )
  {
    mInstances[item]->at(attIndex)->mValue /= (float)tot;
  }
}

Data *Data::clone()
{
	Data *toRet = new Data();
	toRet->read( mFileName );

	return toRet;
}

bool Data::cover( Rule *rule )
{
	vector< vector< InstanceElement * > * >::iterator instItr = mInstances.begin();
	bool removed = false;

	while ( instItr != mInstances.end() )
	{
		if ( rule->isSatisfied( *instItr ) )
		{
			vector< InstanceElement * > *tmp = (*instItr);
			removed = true;
			instItr = mInstances.erase( instItr );
			// Clean up memory to avoid leaks.
			while ( tmp->size() > 0 )
			{
				InstanceElement *ie = tmp->back();
				tmp->pop_back();
				delete ie;
			}
			delete tmp;
		}
		else
		{
			instItr++;
		}
	}

	// Recalculate the class frequencies.
	for ( unsigned int i = 0; i < mClassFreqs.size(); i++ ) mClassFreqs[i] = 0;
	for ( unsigned int i = 0; i < mInstances.size(); i++ )
		mClassFreqs[getClassIndex( mInstances[i] )]++;

	return removed;
}

void Data::calcLift()
{
	mLift = 0;
	for ( unsigned int f = 0; f < mClassFreqs.size(); f++ )
		mLift += mClassFreqs[f] * pow( (double)2, (double)(f+1) );
	mLift /= mInstances.size();
}

void Data::calcPDPFEst( unsigned int LOC )
{
  	if ( LOC < 0 || LOC >= mAtts.size() )
	{
		cerr << LOC << " is out of range. Exiting." << endl;
		exit( 1 );
	}
	if ( !( mIsReal[LOC] ) )
	{
		cerr << "Attribute " << mAtts[LOC] << " is not a continuous attribute. Exiting." << endl;
		exit( 1 );
	}

	mTotLOC = 0;
	mLOCs.resize( mInstances.size() );
	for ( unsigned int i = 0; i < mInstances.size(); i++ )
	{
	  mLOCs[i] = mInstances[i]->at( LOC )->mValue;
	  mTotLOC += mLOCs[i];
	}
}

void Data::calcProbSupt()
{
	// If any attribute is continuous, the data has not been discretized and this would fail, 
	// so exit.
	for ( unsigned int r = 0; r < mIsReal.size(); r++ )
	{
		if ( mIsReal[r] )
		{
			cerr << "Attribute " << mAtts[r] << " is continuous, cannot calculate frequency counts. Exiting." << endl;
			exit( 0 );
		}
	}

	// Create the frequency table.  This is essentially a jagged array.
	mAttrValFreqs.resize( mAtts.size()-1 );
	for ( unsigned int att = 0; att < mAtts.size()-1; att++ ) 
	{
		mAttrValFreqs[att].resize( mAttVals[mAtts[att]].size() );
		for ( unsigned int bore = 0; bore < mAttrValFreqs[att].size(); bore++ )
		{
			mAttrValFreqs[att][bore] = new int[2];
			mAttrValFreqs[att][bore][0] = 0;
			mAttrValFreqs[att][bore][1] = 0;
		}
	}

	// Read the data line by line and count the frequency of best and rest
	// class for each attribute-value pair.
	for ( unsigned int item = 0; item < mInstances.size(); item++ )
	{
	  //cout << getClassIndex( mInstances[item] ) << endl;
	  for ( unsigned int att = 0; att < mAtts.size()-1; att++ )
	  {
	    mAttrValFreqs[att][mInstances[item]->at(att)->mIndex][getClassIndex( mInstances[item] )]++;
	  }
	}
}

float Data::getLift()
{
	return mLift;
}

int Data::getTotLOC()
{
	return mTotLOC;
}

vector< int > Data::getLOCs()
{
	return mLOCs;
}

vector< vector< InstanceElement * > * > Data::getInstanceSet()
{
	return mInstances;
}
unsigned int Data::getNumAtts()
{
	return mAtts.size()-1;
}

unsigned int Data::getNumClasses()
{
	return getNumAttVals( mClassName );
}

unsigned int Data::getClassIndex( vector< InstanceElement * > *instance )
{
	return instance->at( instance->size() - 1 )->mIndex;
}

unsigned int Data::getNumAttVals( string att )
{
	if ( find( att, mAtts ) == -1 )
	{
		cerr << "Attribute " << att << " does not exist!" << endl;
		exit( 0 );
	}

	return mAttVals[att].size();
}

string Data::getAttName( int index )
{
	if ( index >= 0 && index < mAtts.size() )
		return mAtts[index];
	
	cerr << "Index of " << index << " out of range!" << endl;
	exit( 0 );
}

string Data::getAttValName( string att, int index )
{
	if ( find( att, mAtts ) == -1 )
	{
		cerr << "Attribute " << att << " does not exist!" << endl;
		exit( 0 );
	}

	if ( index >= 0 && index < mAttVals[att].size() )
		return mAttVals[att][index];

	cerr << "Index of " << index << " out of range for attribute = " << att << endl;
	exit( 0 );
}

unsigned int Data::getAttIndex( string name )
{
  for ( unsigned int i = 0; i < mAtts.size(); i++ )
  {
    cout << "|" << mAtts[i] << "|" << endl;
    if ( mAtts[i] == name )
      return i;
  }
  return mAtts.size() + 1;
}

unsigned int Data::getAttValIndex( string attName, string valName )
{
  if ( mAttVals[attName].size() ==  0 )
  {
    cerr << attName << " is not a valid attribute name. Exiting." << endl;
    exit( 1 );
  }

  for ( unsigned int i = 0; i < mAttVals[attName].size(); i++ )
  {
    cout << "|" << mAttVals[attName][i] << "|" << endl;
    if ( mAttVals[attName][i] == valName )
      return i;
  }

  return mAttVals[attName].size() + 1;
}

string Data::getClassName( int index )
{
	if ( index >= 0 && index < mAttVals[mClassName].size() )
		return mAttVals[mClassName][index];

	cerr << "Index of " << index << " out of range for class( " << mClassName << " )" << endl;
	exit( 0 );
}

vector< int > Data::getClassFreqs()
{
	return mClassFreqs;
}

const vector< vector< int * > > *Data::getFrequencyTable()
{
	return &mAttrValFreqs;
}

void Data::printAttributes()
{
	for ( unsigned int att = 0; att < mAtts.size()-1; att++ )
	{
		cout << mAtts[att] << ": ";
		if ( mIsReal[att] )
			cout << "continuous";
		else
		{
			cout << mAttVals[mAtts[att]][0];
			for ( unsigned int val = 1; val < mAttVals[mAtts[att]].size(); val ++ )
			{
				cout << ", " << mAttVals[mAtts[att]][val];
				if ( (val+1) % 5 == 0 ) cout << endl;
			}
		}
		cout << endl << endl;
	}

	cout << endl << "Class" << endl;
	cout << mClassName << ": " << mAttVals[mClassName][0];
	for ( unsigned int cVal = 1; cVal < mAttVals[mClassName].size(); cVal++ )
		cout << ", " << mAttVals[mClassName][cVal];
	cout << endl;
}

void Data::printDataSet( ostream &stream )
{
	for ( unsigned int inst = 0; inst < mInstances.size(); inst++ )
	{
	  //if ( mInstances[inst]->at(0)->mIsUnknown ) stream << ",UNKNOWN";
	  /*else*/ if ( mIsReal[0] ) stream << mInstances[inst]->at(0)->mValue;
	  else stream << mAttVals[mAtts[0]][mInstances[inst]->at(0)->mIndex];
	  for ( unsigned int att = 1; att < mAtts.size(); att++ )
	    //if ( mInstances[inst]->at(att)->mIsUnknown ) stream << ",UNKNOWN";
	    /*else*/ if ( mIsReal[att] ) stream << "," << mInstances[inst]->at(att)->mValue;
	    else stream << "," << mAttVals[mAtts[att]][mInstances[inst]->at(att)->mIndex];
	  stream << endl;
	}
}

void Data::printClassDist()
{
	for ( unsigned int c = 0; c < mAttVals[mClassName].size(); c++ )
		cout << mAttVals[mClassName][c] << ": " << mClassFreqs[c] << "[ " << mClassFreqs[c]/(float)mInstances.size() << " ]" << endl;
}

void Data::printInstance( int inst )
{
	// If inst is out of range, print message and exit.
	if ( inst < 0 || inst > mInstances.size() )
	{
		cerr << inst << " is out of range, exiting." << endl;
		exit( 0 );
	}

	cout << mAttVals[mAtts[0]][mInstances[inst]->at(0)->mIndex];
	for ( unsigned int i = 1; i < mInstances[inst]->size(); i++ )
	{
		if ( (i+1) % 4 == 0 ) cout << endl;
		cout << ", " << mAttVals[mAtts[i]][mInstances[inst]->at(i)->mIndex];
	}
	cout << endl << endl;
}

void Data::printFrequencyTable( ostream &stream )
{
	cout << "<attribute>: <value_1>( rest_count, best_count ), ..." << endl;
	cout << "-----------------------------------------------------" << endl;
	for ( unsigned int att = 0; att < mAttrValFreqs.size(); att++ )
	{
		stream << mAtts[att] << ": " << mAttVals[mAtts[att]][0] << "( " << mAttrValFreqs[att][0][0] << ", " 
			   << mAttrValFreqs[att][0][1] << " )";
		for ( unsigned int val = 1; val < mAttrValFreqs[att].size(); val++ )
		{
			if ( (val+1)%6 == 0 ) stream << "\t\t" << endl;
			stream << ", " << mAttVals[mAtts[att]][val] << "( " << mAttrValFreqs[att][val][0] << ", " 
				   << mAttrValFreqs[att][val][1] << " )";
		}
		stream << endl;
	}
}

void Data::processAttribute( std::string line )
{
	string name = line.substr( line.find( "@attribute" ) + 11 );
	name = name.substr( name.find_first_not_of( " " ) );
	//cout << "|" << name << "|" << endl;
	string vals = name.substr( name.find( " " ) );
	vals = vals.substr( vals.find_first_not_of( " " ) );
	//cout << "|" << vals << "|" << endl;
	string test;
	bool done = false;

	name = name.substr( 0, name.find( vals ) );
	mAtts.push_back( name );
	vals = vals.substr( vals.find_first_of( " " ) + 1 );
	test = vals.substr( 0, vals.find_last_of( " " ) );
	// If the attribute is real number, set the flag that says so and exit.
	if ( test.compare( "real" ) == 0 || test.compare( "number" ) == 0 ||
		 test.compare( "integer" ) == 0 || test.compare( "continuous" ) == 0 ||
		 test.compare( "numeric" ) == 0 )
	{
		mIsReal.push_back( true );
		return;
	}
	mIsReal.push_back( false );
	vals = vals.substr( vals.find( "{" )+1 );
	vals = vals.substr( 0, vals.find( "}" ) );
	while ( !done )
	{
		int index = vals.find( "," ); 
		if ( index == string::npos ) 
		{
			index = vals.length();
			done = true;
		}
		string val = vals.substr( 0, index);
		if ( !done ) vals = vals.substr( index+1 );
		while ( val[0] == ' ' ) val = val.substr( 1 );
		mAttVals[name].push_back( val );
	}
}

void Data::processInstance( std::string line )
{
        if ( line.find( "?" ) != string::npos ) return;

	int index;
	InstanceElement *ie;
	vector< InstanceElement * > *instance = new vector< InstanceElement * >();
	stringstream ss(stringstream::in | stringstream::out);
	for ( unsigned int i = 0; i < mAtts.size()-1; i++ )
	{
		string val = line.substr( 0, line.find( "," ) );

		index = find( val, mAttVals[mAtts[i]] );
		//if ( val == "?" )
		//{
		//  ie = new InstanceElement();
		//  ie->mIsUnknown = true;
		//}
		/*else*/ if ( mIsReal[i] )
		{
			ie = new InstanceElement();
			while ( val[0] == ' ' ) val = val.substr( 1 );
			ss << val << endl;
			ss >> ie->mValue;
			//ie->mIsUnknown = false;
			instance->push_back( ie );

		}
		else if ( index != -1 ) 	
		{
			ie = new InstanceElement();
			ie->mIndex = index;
			//ie->mIsUnknown = false;
			instance->push_back( ie );
		}
		else
		{
			cerr << "Data file corrupt." << endl;
			cerr << "\'" << val << "\' is not a part of " << mAtts[i] << endl;
			exit( 0 );
		}

		line = line.substr( line.find( "," ) + 1 );
	}

	index = find( line, mAttVals[mClassName] );
	if ( index != -1 ) 
	{
		ie = new InstanceElement();
		ie->mIndex = index;
		//ie->mIsUnknown = false;
		instance->push_back( ie );
		mClassFreqs[index]++;
	}
	else
	{
		cerr << "Data file corrupt." << endl;
		cerr << "\'" <<line << "\'" << " is not a valid class value." << endl;
		exit( 0 );
	}

	mInstances.push_back( instance );
}

string Data::preprocessString( string line )
{
	int pos = line.find( ", " );
	for ( unsigned int i = 0; i < line.length(); i++ )
		if ( line[i] == '\t' ) line[i] = ' ';

	// Turn situations like @attribute a1 {1,    2,    3,    4}
	// into @attribute a1 {1,2,3,4}
	while ( pos != string::npos )
	{
		while ( pos+1 < line.length() && line[pos+1] == ' ' )
			line = line.erase( pos+1, 1 );
		pos = line.find( ", " );
	}

	return line;
}

int Data::find( string att, vector<string> &l)
{
	for ( unsigned int i = 0; i < l.size(); i++ )
		if ( att.compare( l[i] ) == 0 )
			return i;

	return -1;
}
