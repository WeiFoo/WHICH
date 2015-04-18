#include "Rule.h"
#include "Data.h"
#include "defines.h"
#include "WhichStack.h"
#include <cmath>
using namespace std;

Rule::Rule()
{
	mAlpha = 1;
	mBeta = 1000;
	mGamma = 1;
	mGamma = 0;
	mPD = mPF = mEffort = mProbBest = mProbRest = 0;
	mSize = 1;
	mTargetClass = 1;
	mComponent = NULL;
}

Rule::Rule( int attribute, int value, Data *d, RULE_TYPE type, float (*scoreFcn)( Rule * ) )
{
  mPicked.push_back( new DisjunctionSet() );
  mPicked[0]->mAttribute = attribute;
  mPicked[0]->mValues.push_back( value );
  mScoreFcn = scoreFcn;
  mData = d;
  mType = type;

  mAlpha = 1;
  mBeta = 1000;
  mGamma = 1;
  mGamma = 0;
  mPD = mPF = mEffort = mProbBest = mProbRest = 0;
  mSize = 1;
  mTargetClass = 1;  
  mComponent = NULL;
}

Rule::~Rule()
{
	DisjunctionSet *d;
	while ( mPicked.size() > 0 )
	{
		d = mPicked.back();
		mPicked.pop_back();
		delete d;
	}
	delete mComponent;
}

void Rule::setData( Data *d ) { mData = d; }

void Rule::setWeights( float alpha, float beta, float gamma )
{
	mAlpha = alpha;
	mBeta = beta;
	mGamma = gamma;
}


float Rule::getScore() { return mScore; }
float Rule::getSupport() { return mSupport; }
float Rule::getPD() { return mPD; }
float Rule::getPF() { return mPF; }
float Rule::getEffort() { return mEffort; }
int Rule::getSize() { return mSize; }
void *Rule::getComponent() { return mComponent; }
void Rule::setComponent( void *com ) { mComponent = com; }
vector< DisjunctionSet * > *Rule::getRuleSet() { return &mPicked; }

Rule *Rule::clone()
{
	Rule *toRet = new Rule();
	for ( unsigned int att = 0; att < mPicked.size(); att++ )
	{
		toRet->mPicked.push_back( new DisjunctionSet() );
		toRet->mPicked[att]->mAttribute = mPicked[att]->mAttribute;
		for ( unsigned int val = 0; val < mPicked[att]->mValues.size(); val++ )
			toRet->mPicked[att]->mValues.push_back( mPicked[att]->mValues[val] );
	}
	
	toRet->mData = mData;
	toRet->mSize = mSize;
	toRet->mScore = mScore;
	toRet->mSupport = mSupport;
	toRet->mProbBest = mProbBest;
	toRet->mProbRest = mProbRest;
	toRet->mEffort = mEffort;
	toRet->mPD = mPD;
	toRet->mPF = mPF;
	toRet->mAlpha = mAlpha;
	toRet->mBeta = mBeta;
	toRet->mGamma = mGamma;
	toRet->mTargetClass = mTargetClass;
	toRet->mScoreFcn = mScoreFcn;
	toRet->mComponent = NULL;

	return toRet;
}

bool Rule::createFromFile( string fName, Data *data, RULE_TYPE type, float (*scoreFcn)( Rule * ) )
{
  ifstream rFile( fName.c_str() );
  int attVal[2] = { -1, -1 };
  string tok, att;
  bool ruleCreated = false;

  if ( !rFile.is_open() )
  {
    cerr << "File " << fName << " could not be open.  Exiting." << endl;
    exit( 1 );
  }

  mData = data;
  mType = type;
  mScoreFcn = scoreFcn;
  
  rFile >> tok;
  while ( tok != "END" )
  {
    if ( attVal[0] == -1 )
    {
      att = tok +  ' ';
      attVal[0] = mData->getAttIndex( att );
      if ( attVal[0] == mData->getNumAtts() + 1 )
      {
	cerr << att << " was found in " << fName << " but not in the Data set. Exiting" << endl;
	exit( 1 );
      }
      cout << attVal[0] << endl;
    }
    else
    {
      attVal[1] = mData->getAttValIndex( att, tok );
      if ( attVal[1] == mData->getNumAttVals( att ) )
      {
	cerr << tok << " was foind in " << fName << " but not in the Data set. Exiting." << endl;
	exit( 1 );
      }
      addComponent( attVal[0], attVal[1] );
      ruleCreated = true;
      attVal[0] = -1;
    }
    rFile >> tok;
  }

  score();

  return ruleCreated;
}

float Rule::compare( Rule *r )
{
	return mScore - r->mScore;
}

bool Rule::isSatisfied( vector< InstanceElement * > *instance )
{
	Rule *r = new Rule();
	for ( unsigned int i = 0; i < instance->size() - 1; i++ )
	  //if ( !( instance->at(i)->mIsUnknown ) )
	    r->addComponent( i, instance->at(i)->mIndex );

	for ( unsigned int att = 0; att < mPicked.size(); att++ )
		for ( unsigned int val = 0; val < mPicked[att]->mValues.size(); val++ )
			if ( !( r->hasComponent( mPicked[att]->mAttribute, mPicked[att]->mValues[val] ) ) )
			{
				delete r;
				return false;
			}

	delete r;
	return true;
}

void Rule::score()
{
  	switch( mType )
	{
		case LIFT: scoreLift(); break;
		case EFFORT: scoreEffort(); break;
		case PROBSUPT: scoreProbSupt(); break;
		case INFOGAIN: scoreInfoGain(); break;
		case PDPF: scorePDPF(); break;
		case PDOVEREFFORT: scorePDOverEffort(); break;
	        case PDOVERLOC: scorePDOverLOC(); break;
	        case SPECIAL: scoreSpecial(); break;
		default: scoreInfoGain(); break;
	}
	//mScore *= 100;
}

void Rule::scoreLift()
{
	vector< vector< InstanceElement * > * > instances = mData->getInstanceSet();
	vector< int > freqs( mData->getNumClasses() );
	mScore = 0;
	int totInst = 0;
	mPD = mPF = 0;

	for ( unsigned int c = 0; c < freqs.size(); c++ ) freqs[c] = 0;
	for ( unsigned int i = 0; i < instances.size(); i++ )
		if ( isSatisfied( instances[i] ) )
		{
			freqs[mData->getClassIndex( instances[i] )]++;
			if ( mData->getClassIndex( instances[i] ) == mTargetClass ) mPD++;
			else mPF++;
			totInst++;
		}
	
	for ( unsigned int i = 0; i < freqs.size(); i++ )
		mScore += freqs[i] * pow( (double)2, (double)(i+1) );

	if ( totInst == 0 || mData->getLift() == 0 ) mScore = 0;
	else mScore = mScore/(float)totInst/(float)mData->getLift();
	
	if ( instances.size() == 0 ) mSupport = 0;
	else mSupport = totInst/(float)instances.size() * 100;

	if ( mSupport < 0 || mScore < 0.001 ) mScore = 0.0;
	mPD = mPD/(float)mData->getClassFreqs()[mTargetClass];
	mPF = mPF/(float)mData->getClassFreqs()[0];
}

float Rule::calcDist()
{
	return sqrt( (double)mPD * mPD * mAlpha +
				 (1-mPF) * (1-mPF) * mBeta +  
				 (1-mEffort) * (1-mEffort) * mGamma ) / 
				 sqrt( (double)mAlpha + mBeta + mGamma );
}

void Rule::scoreEffort()
{
	vector< vector< InstanceElement * > *> instances = mData->getInstanceSet();
	vector< int > LOCs = mData->getLOCs();
	int freqBest = 0, freqRest = 0;
	mPD = mPF = mEffort = 0;

	for ( unsigned int item = 0; item < instances.size(); item++ )
	{
		if ( isSatisfied( instances[item] ) )
		{
			mEffort += LOCs[item];
			if ( mData->getClassIndex( instances[item] ) == mTargetClass ) freqBest++;
			else freqRest++;
		}
	}

	if ( mData->getTotLOC() <= 0 ) mEffort = 0;
	else mEffort /= (float)mData->getTotLOC();

	if ( mData->getClassFreqs().back() <= 0 ) mPD = 0;
	else mPD = freqBest/(float)mData->getClassFreqs()[mTargetClass];

	if ( freqBest + freqRest <= 0 )  mPF = 0;
	else mPF = freqRest/(float)(freqBest + freqRest ); // PF = FP/(FP +TN) = freqRest/(freqRest + TN)!!!!

	if ( mData->getClassFreqs().back() <= 0 ) mSupport = 0;
	else mSupport = freqBest/(float)(mData->getClassFreqs().back()) * 100;

	if ( mPD <= .2 || mPF > 0.8 || mEffort > 0.8 ) mScore = 0.0;
	else mScore = calcDist();
}

void Rule::scoreProbSupt()
{
	const vector< vector< int* > > *freqTable = mData->getFrequencyTable();
	int restCnt = mData->getClassFreqs()[0], bestCnt = mData->getClassFreqs()[1]; 
	mProbBest = mProbRest = 1;
	
	for ( unsigned int att = 0; att < mPicked.size(); att++ )
	{
		int restSum = 0, bestSum = 0;
		for ( unsigned int val = 0; val < mPicked[att]->mValues.size(); val++ )
		{
			restSum += freqTable->at( mPicked[att]->mAttribute )[ mPicked[att]->mValues[val]][0];
			bestSum += freqTable->at( mPicked[att]->mAttribute )[ mPicked[att]->mValues[val]][1];
		}
		if ( restSum + bestSum == 0 )
		{
			mProbRest = 0;
			mProbBest = 0;
		}
		else
		{
			mProbRest *= restSum/(float)( restSum + bestSum );
			mProbBest *= bestSum/(float)( restSum + bestSum );
		}
	}

	if ( restCnt == 0 ) mProbRest = 0;
	else mProbRest /= (float)( restCnt );

	if ( bestCnt == 0 ) mProbBest = 0;
	else mProbBest /= (float)( bestCnt );

	if ( mProbBest + mProbRest  == 0 ) mScore = 0;
	else mScore = ( mProbBest * mProbBest )/(float)( mProbBest + mProbRest );

	mPD = mProbBest;
	mPF = mProbRest;
	mSupport = mProbBest;
}

void Rule::scoreInfoGain()
{
	int *classFreqs = new int[mData->getNumClasses()];
	int numHit = 0;
	vector< vector< InstanceElement * > * > data = mData->getInstanceSet();

	// Initialize the frequency counts to zero.
	mScore = 0;
	for ( int c = 0; c < mData->getNumClasses(); c++ ) classFreqs[c] = 0;

	// Get the class counts of the instances of data this rule hits.
	for ( unsigned int item = 0; item < data.size(); item++ )
		if ( isSatisfied( data[item] ) )
		{
			classFreqs[ mData->getClassIndex( data[item]) ]++;
			numHit++;
		}
	
	// Get this entropy for this Rule.
	if ( numHit > 0 )
	{
		for ( int c = 0; c < mData->getNumClasses(); c++ )
			if ( classFreqs[c] != 0 )
			{
				float a = -( classFreqs[c]/(float)numHit );
				float b = log( -a )/log( 2.0 );
				mScore += a * b;
			}
		mSupport = numHit/(float)data.size();
		mScore = 100 - mScore;
	}
}

void Rule::scorePDPF()
{
	int bestCnt = 0, restCnt = 0;
	for ( unsigned int item = 0; item < mData->getInstanceSet().size(); item++ )
	{
		if ( isSatisfied( mData->getInstanceSet()[item] ) )
		{
			if ( mData->getClassIndex( mData->getInstanceSet()[item] ) == mTargetClass ) bestCnt++;
			else restCnt++;
		}
	}

	mPD = bestCnt/(float)( mData->getClassFreqs()[mTargetClass] );
	mPF = restCnt/(float)( mData->getClassFreqs()[0] );
	mSupport = mPD;
	mScore = sqrt( mPD * mPD * mAlpha + (1-mPF) * (1-mPF) * mBeta )/sqrt( mAlpha + mBeta ) * 100;
}

void Rule::scorePDOverEffort()
{
	float bestCnt = 0, restCnt = 0, totLoc = 0;
	for ( unsigned int item = 0; item < mData->getInstanceSet().size(); item++ )
	{
		if ( isSatisfied( mData->getInstanceSet()[item] ) )
		{
			if ( mData->getClassIndex( mData->getInstanceSet()[item] ) == mTargetClass ) bestCnt++;
			else restCnt++;
			totLoc += mData->getLOCs()[item];
		}
	}

	mPD = bestCnt/(float)( mData->getClassFreqs()[mTargetClass] );
	mPF = restCnt/(float)( mData->getClassFreqs()[0] );
	if ( mData->getTotLOC() > 0 ) mEffort = totLoc/(float)( mData->getTotLOC() );
	else mEffort = 0;
	mSupport = mPD;
	if ( mEffort > 0 ) mScore = ( mPD ) / mEffort;
	else mScore = 0;
}

void Rule::scorePDOverLOC()
{
  scorePDOverEffort();
  mEffort *= mData->getTotLOC();
  if ( mPD == 0 && mEffort == 0) mScore = 0;
  else if ( mEffort == 0 ) mScore = mPD;
  else mScore = mPD/(float)mEffort;    
}

void Rule::scoreRipper()
{
  int p, n;
  scorePDOverLOC();
  mEffort = 0;
  p = mPD * mData->getClassFreqs()[1];
  n = mPF * mData->getClassFreqs()[0];
  if ( p + n  == 0 ) mScore = 0;
  else mScore = (float)p/(float)(p+n) - (float)n/(float)(p+n);
}

void Rule::scorePrecision()
{
  int p, n;
  scorePDOverLOC();
  mEffort = 0;
  p = mPD * mData->getClassFreqs()[1];
  n = mPF * mData->getClassFreqs()[0];
  if ( p + n  == 0 ) mScore = 0;
  else mScore = (float)p/(float)(p+n);
}

void Rule::scoreSpecial()
{
  mScore = mScoreFcn( this );
}

int Rule::findAttribute( int attribute )
{
	for ( unsigned int att = 0; att < mPicked.size(); att++ )
		if ( mPicked[att]->mAttribute == attribute )
			return att;

	return -1;
}

int Rule::findAttributeValue( int attribute, int value )
{
	int att = findAttribute( attribute );
	if ( att == -1 ) return -1;

	for ( unsigned int val = 0; val < mPicked[att]->mValues.size(); val++ )
		if ( mPicked[att]->mValues[val] == value )
			return val;

	return -1;
}

bool Rule::hasComponent( int attribute, int value )
{
	for ( unsigned int att = 0; att < mPicked.size(); att++ )
		if ( mPicked[att]->mAttribute == attribute )
			for ( unsigned int val = 0; val < mPicked[att]->mValues.size(); val++ )
				if ( mPicked[att]->mValues[val] == value )
					return true;

	return false;
}

bool Rule::isEqualTo( Rule *r )
{
	// If the rules don't have the same conjunctions, they can't be equal.
	if ( mPicked.size() != r->mPicked.size() ) return false;

	for ( unsigned int att = 0; att < mPicked.size(); att++ )
	{
		int rAtt = r->findAttribute( mPicked[att]->mAttribute );

		// If this attribute doesn't exist in r, they can't be equal.
		if ( rAtt == -1 ) return false;

		// If this attribute's disjuntions aren't the same size as r's, they can't be equal.
		if ( this->mPicked[att]->mValues.size() != r->mPicked[rAtt]->mValues.size() ) return false;

		// If we are here, that means that Rule r has the same number of attributes.
		// the current attribute is in r, and that the number of disjunctions in r
		// are the same as this one's.  now we much check to see if the actual indexes match.
		for ( unsigned int val = 0; val < mPicked[att]->mValues.size(); val++ )
			if ( r->findAttributeValue( mPicked[att]->mAttribute, mPicked[att]->mValues[0] ) == -1 )
				return false;
	}

	return true;
}

bool Rule::addComponent( int attribute, int value )
{
	int attLoc = findAttribute( attribute );
	if ( attLoc != -1 )
	{
		if ( findAttributeValue( attribute, value ) != -1 ) return false;
		else mPicked[attLoc]->mValues.push_back( value );
	}
	else
	{
		mPicked.push_back( new DisjunctionSet() );
		mPicked.back()->mAttribute = attribute;
		mPicked.back()->mValues.push_back( value );
	}

	mSize++;
	return true;
}

Rule *Rule::combine( Rule *r )
{
	Rule *toRet = clone();
	vector< DisjunctionSet *>::iterator ai;

	// Combine Rule r with this
	if ( r == NULL ) return toRet;
	for ( unsigned int att = 0; att < r->mPicked.size(); att++ )
		for ( unsigned int val = 0; val < r->mPicked[att]->mValues.size(); val++ )
			toRet->addComponent( r->mPicked[att]->mAttribute, r->mPicked[att]->mValues[val] );

	// If a set of DisjunctionSet covers every attribute range for an attribute, remove that
	// DisjunctionSet from the new Rule.
	ai = toRet->mPicked.begin();
	while ( ai != toRet->mPicked.end() && mData != NULL )
	{
		if ( (*ai)->mValues.size() == mData->getNumAttVals( mData->getAttName( (*ai)->mAttribute ) ) )
		{
			toRet->mSize -= (*ai)->mValues.size();
			ai = toRet->mPicked.erase( ai );
		}
		else
			ai++;
	}

	toRet->mData = mData;
	toRet->mType = mType;
	return toRet;
}

Rule *Rule::backSelect()
{
	Rule *w, *toRet;
	vector< DisjunctionSet *>::iterator attItr;
	vector< int >::iterator valItr;
	int att, val;

	// Get the lowest scoring attr-val pair.
	for ( unsigned int att = 0; att < mPicked.size(); att++ )
	{
		for ( unsigned int val = 0; val < mPicked[att]->mValues.size(); val++ )
		{
			Rule *r = new Rule( mPicked[att]->mAttribute, mPicked[att]->mValues[val], mData, mType );
			r->score();
			if ( att == 0 && val == 0 ) w = r;
			else if ( r->mScore < w->mScore )
			{
				delete w;
				w = r;
			}
			else delete r;
		}
	}

	toRet = clone();

	att = toRet->findAttribute( w->mPicked[0]->mAttribute );
	val = toRet->findAttributeValue( w->mPicked[0]->mAttribute, w->mPicked[0]->mValues[0] );
	attItr = toRet->mPicked.begin();
	valItr = toRet->mPicked[att]->mValues.begin();
	for ( unsigned int a = 0; a < att; a++ ) attItr++;
	for ( unsigned int v = 0; v < val; v++ ) valItr++;

	toRet->mPicked[att]->mValues.erase( valItr );
	toRet->mSize--;
	if ( toRet->mPicked[att]->mValues.size() == 0 )
	{
		DisjunctionSet *ds = *attItr;
		toRet->mPicked.erase( attItr );
		delete ds;
	}

	toRet->score();
	if ( toRet->mScore > mScore ) return toRet;
	else 
	{
		delete toRet;
		return NULL;
	}
}

void Rule::printGotWant( ostream& stream, Data *eData )
{
	int hit = 0;
	vector< vector< InstanceElement * > * > items = mData->getInstanceSet();
	for ( unsigned int item = 0; item < items.size(); item++ )
	{
		if ( isSatisfied( items[item] ) )
		{
			hit++;
			stream << hit << " " << mData->getClassName( mTargetClass ) 
				   << " xxx " << mData->getClassName( eData->getClassIndex( items[item] ) ) 
				   << " (" << eData->getLOCs()[item] << ")" << endl;
		}
	}
}

void Rule::print( ostream &stream )
{
	for ( unsigned int att = 0; att < mPicked.size(); att++ )
	{
		if ( att != 0 ) 
		{
			stream << "AND ";
			stream.width( 26 );
		}
		else stream.width( 30 );
		stream.flags( ios::left );
		stream << mData->getAttName( mPicked[att]->mAttribute );
		stream << " = [ ";
		for ( unsigned int val = 0; val < mPicked[att]->mValues.size(); val++ )
		{
			if ( val != 0 ) stream << " OR ";
			stream << mData->getAttValName( mData->getAttName(  mPicked[att]->mAttribute )
				     , mPicked[att]->mValues[val] ) << "(" << mPicked[att]->mValues[val]+1 << ")";
		}
		stream << " ]" << endl;
	}
	stream << "Score:" << mScore << endl;
	stream << "PD:" << mPD << endl;
	stream << "PF:" << mPF << endl;
}

void Rule::printRule( ostream& stream )
{
	for ( unsigned int att = 0; att < mPicked.size(); att++ )
	{
		string conj = att == 0 ? "" : " AND ";
		stream << conj << mData->getAttName( mPicked[att]->mAttribute ) << " = [ ";
		for ( unsigned int val = 0; val < mPicked[att]->mValues.size(); val++ )
		{
			string disj = val == 0 ? "" : " OR ";
			stream << disj << mData->getAttValName( mData->getAttName( mPicked[att]->mAttribute ),
													mPicked[att]->mValues[val] );
		}
		stream << " ]";
		if ( (att+1) % 4 == 0 ) stream << endl << "\t\t";
	}
	stream << endl;
}
