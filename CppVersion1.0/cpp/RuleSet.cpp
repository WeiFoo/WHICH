#include "RuleSet.h"
#include "Data.h"
#include "WhichStack.h"
#include "defines.h"
using namespace std;

RuleSet::RuleSet(){}

RuleSet::RuleSet( Data *train, Data *test, RULE_TYPE type )
{
	mTrain = train;
	if ( test != NULL ) mTest = test;
	else mTest = mTrain;
	mType = type;
	mAlpha = mBeta = 1;
	mGamma = 0;
	mConfusionMatrix[0][0] = mConfusionMatrix[0][1] = mConfusionMatrix[1][0] = mConfusionMatrix[1][1] = 0;
}

RuleSet::~RuleSet()
{
	while ( mRules.size() > 0 )
	{
		Rule *r = mRules.back();
		mRules.pop_back();
		delete r;
	}
}

void RuleSet::create()
{
	Data *tmp = mTrain->clone();
	tmp->calcProbSupt();
	tmp->calcLift();

	while ( tmp->getClassFreqs()[1]/(float)(mTrain->getInstanceSet().size()) > 0.05 )
	{
		WhichStack *stack = new WhichStack( INFINITY );
		stack->create( tmp, mType, 1, 1, 0 );
		stack->select( 2000, 200, 0.2 );

		mRules.push_back( stack->getBest()->clone() );
		//cout << tmp->getInstanceSet().size() << endl;
		//stack->getBest()->print( cout << "Stack: " );
		tmp->cover( stack->getBest() );
		delete stack;
	}

	delete tmp;
}

void RuleSet::score()
{
	mConfusionMatrix[0][0] = mConfusionMatrix[0][1] = mConfusionMatrix[1][0] = mConfusionMatrix[1][1] = 0;
	Data *tmp = mTest->clone();

	for ( unsigned int rule = 0; rule < mRules.size(); rule++ )
	{
		vector< vector< InstanceElement * > * > items = tmp->getInstanceSet();
		for ( unsigned int item = 0; item < items.size(); item++ )
		{
			if ( mRules[rule]->isSatisfied( items[item] ) )
			{
				if ( tmp->getClassIndex( items[item] ) == 1 ) mConfusionMatrix[1][1]++;
				else mConfusionMatrix[0][1]++;
			}
		}
		tmp->cover( mRules[rule] );
	}

	mConfusionMatrix[0][0] = tmp->getClassFreqs()[0];
	mConfusionMatrix[1][0] = tmp->getClassFreqs()[1];

	delete tmp;
}

void RuleSet::print( std::ostream &stream )
{
	stream << "Generated " << mRules.size() << " rules." << endl;
	for ( unsigned int rule = 0; rule < mRules.size(); rule++ )
	{
		mRules[rule]->setData( mTest );
		mRules[rule]->printRule( stream );
	}
	
	float pd = 0, pf = 0;
	if ( mConfusionMatrix[1][1] +  mConfusionMatrix[0][1] > 0 )
		pd = mConfusionMatrix[1][1] / (float)( mConfusionMatrix[1][1] + mConfusionMatrix[0][1] );
	if ( mConfusionMatrix[1][0] +  mConfusionMatrix[0][0] > 0 )
		pf = mConfusionMatrix[1][0] / (float)( mConfusionMatrix[1][0] + mConfusionMatrix[0][0] );

	cout << endl;
	cout << "\t" << mTrain->getClassName( 0 ) << "\t" << mTrain->getClassName( 1 ) << "  <-- Actual" << endl;
	cout << "Silent\t" << mConfusionMatrix[0][0] << "\t" << mConfusionMatrix[0][1] << endl;
	cout << "Loud\t" << mConfusionMatrix[1][0] << "\t" << mConfusionMatrix[1][1] << endl << endl;
	stream << "PD = " << pd << endl;
	stream << "PF = " << pf << endl << endl;
}