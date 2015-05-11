#include "WhichStack.h"
#include "Rule.h"
#include "Data.h"
#include "defines.h"
#include <cmath>
#include <vector>
using namespace std;

WhichStack::WhichStack()
{
	mMaxSize = INFINITY;
}

WhichStack::WhichStack( int maxSize )
{
	mMaxSize = maxSize;
}

WhichStack::~WhichStack()
{
	Rule *r;
	while ( mRules.size() > 0 )
	{
		r = mRules.back();
		mRules.pop_back();
		delete r;
	}
}

void WhichStack::create( Data *data, int type, float alpha, float beta, float gamma )
{
  RULE_TYPE t = (RULE_TYPE)type;
	for ( unsigned int att = 0; att < data->getNumAtts(); att++ )
	{
		for ( unsigned int val = 0; val < data->getNumAttVals( data->getAttName( att ) ); val++ )
		{
			Rule *r = new Rule( att, val, data, t ); 
			r->setWeights( alpha, beta, gamma );
			r->score();
			if ( !( push( r ) ) ) delete r;
		}
	}
}

bool WhichStack::push( int attval[], float (*scoreFcn)( Rule * ) )
{
  Rule *r = new Rule( attval[0], attval[1], NULL, SPECIAL, scoreFcn );
  r->score();

  if ( !push( r ) ) delete r;

  return true;
}

int WhichStack::select( int count, int check, float improve )
{
  int currCount = 0;
  bool noIncrease = false;
  Rule *oldBest, *newBest;
  
  if ( size() <= 0 ) return 0;

  oldBest = getBest();
  while ( !noIncrease && currCount < count )
  {
    pickTwo();

    if ( check > 0 && ( currCount + 1 ) % check == 0 )
    {
      newBest = getBest();
      noIncrease = newBest->getScore()/oldBest->getScore() - 1.0 < improve;
      oldBest = getBest();
    }
    currCount++;
  }
  
  return currCount;
}

bool WhichStack::contains( Rule *r )
{
	for ( unsigned int i = 0; i < mRules.size(); i++ )
		if ( mRules[i]->isEqualTo( r ) )
			return true;

	return false;
}

int WhichStack::pick( vector< float > scores, float sum )
{
	float x = randomNum( 0, sum );
	for ( unsigned int i = 0; i < mRules.size(); i++ )
	{
		if ( x < scores[i] )
			return i;
		x -= scores[i];
	}
    return -1;
}

bool WhichStack::push( Rule *r )
{
	static int i = 0;
	bool wasInserted = false;
	
	if ( contains( r ) )
	{
		return false;
	}
	if ( mRules.size() == 0 ) 
		mRules.push_back( r );
	else if ( r->getScore() < mRules.back()->getScore() && mMaxSize > mRules.size() && mMaxSize != INFINITY )
	{
		mRules.push_back( r );
	}
	else
	{
		for ( vector< Rule * >::iterator ri = mRules.begin(); ri < mRules.end() && !wasInserted; ri++ )
		{
			Rule *current = *ri;
			if ( r->compare( current ) > 0 ||
				 ( r->compare( current ) == 0 && r->getSize() < current->getSize() ) ) // the same score but fewer length
			{
				ri = mRules.insert( ri, r );
				wasInserted = true;
			}
		}
		// If we didn't get in and the WhichStack is full, we are done.
		if ( !wasInserted && mRules.size() >= mMaxSize && mMaxSize != INFINITY ) return false;
		if ( !wasInserted && ( mRules.size() < mMaxSize || mMaxSize != INFINITY ) ) mRules.push_back( r );
		if ( wasInserted && mRules.size() >= mMaxSize && mMaxSize != INFINITY )
		{
			Rule *back = mRules.back();
			mRules.pop_back();
			delete back;
		}
	}

	return true;
}

bool WhichStack::pickTwo()
{
	vector< float > scores( mRules.size() );
	Rule *r;
	int first, second;
	float sum, smallestVal;

	// If the WhichStack has 1 or 0 elements, this can't do anything, so return failure.
	if ( mRules.size() <= 1 ) return false;
	// If there are less than 5 things, just combine them all and see if anything happens.
	else if ( mRules.size() < 5 )
	{
		bool worked = false;
		for ( unsigned int i = 0; i < mRules.size(); i++ )
			for ( unsigned int j = 0; j < mRules.size(); j++ )
				if ( j != i )
				{
					Rule *c = mRules[i]->combine( mRules[j] );
					c->score();
					if ( push( c ) ) worked = true;
				}
		return worked;
	}

	// Otherwise, do a standard weighted stochastic picking of two items.
	// To allow for negative scoring, find the lowest negative value
	// and shift it and all other scores up to make the lowest value 0.00001.
	smallestVal = scores[0];
	for ( unsigned int curRule = 1; curRule < mRules.size(); curRule++ )
	  smallestVal = min( smallestVal, scores[curRule] );

	scores[0] = mRules[0]->getScore();
	sum = scores[0];

	for ( unsigned int curRule = 1; curRule < mRules.size(); curRule++ )
	{
	  scores[curRule] = mRules[curRule]->getScore() + scores[curRule-1] + smallestVal + 0.0001;
	  sum += scores[curRule];
	}

	first = pick( scores, sum );
	// Keep picking a stack item over until it is not the first stack item picked.
	// This prevents a combine of the same rule which gives us nothing.
	do
	{
		second = pick( scores, sum );
	} while ( first == second );

	r = mRules[first]->combine( mRules[second] );
	r->score();

	if ( push( r ) ) 
	{
		// If this new Rule is at the top of the WhichStack, attempt to
		// do a greedy back-select on it until the smaller Rules
		// aren't scoring as well as the bigger ones.
		if ( false && r->isEqualTo( mRules.front() ) && r->getSize() > 1 )
		{
			Rule *bs = r->backSelect();
			while ( bs != NULL )
			{
				push( bs );
				bs = bs->backSelect();
			}
		}
		return true;
	}
	else
	{
		delete r;
		return false;
	}
}

unsigned int WhichStack::size()
{
	return mRules.size();
}

Rule *WhichStack::getBest()
{
	return mRules.front();
}

Rule *WhichStack::getRule( int index )
{
  if ( index < 0 || index >= mRules.size() )
  {
    cerr << index << " is out of range, exiting." << endl;
    exit( 0 );
  }

  return mRules[index];
}

ostream &WhichStack::report( ostream &stream, int n )
{
	for ( unsigned int i = 0; i < n && i < mRules.size(); i++ )
	{
		mRules[i]->print( stream );
		stream << endl;
	}
	return stream;
}

void WhichStack::print( ostream& stream )
{
	for ( unsigned int i = 0; i < mRules.size(); i++ )
	{
		mRules[i]->print( stream );
		stream << endl;
	}
}
