#ifndef RULE_SET_H_
#define RULE_SET_H_

#include "Rule.h"
#include "Data.h"
#include <vector>
#include <iostream>

class Data;

/**
 * This class represents a collection of Rules that are meant to cover an entire
 * data set.
**/
class RuleSet
{
	public:
		/**
		 * Empty Constructor.
		**/
		RuleSet();

		/**
		 * Creates a basic RuleSet. train and test MUST be discrete already.
		 * @param train The data set this RuleSet will train on.
		 * @param test The data set this RuleSet will evaulate on. Passing NULL will result in
		 * the RuleSet being evaulated on the test data.
		 * @param type The type of Rules this RuleSet contains.
		**/
		RuleSet( Data *train, Data *test, RULE_TYPE type );

		/**
		 * Destructor.
		**/
		~RuleSet();

		/**
		 * Creates a series of Rules that attempt to best cover the Data.
		**/
		void create();

		/**
		 * Scores the RuleSet.
		**/
		void score();

		/**
		 * Prints the RuleSet.
		 * @param stream The stream to print to.
		**/
		void print( std::ostream& stream );

	protected:
		std::vector< Rule * > mRules;
		RULE_TYPE mType;
		Data *mTrain, *mTest;
		float mAlpha, mBeta, mGamma;
		int mConfusionMatrix[2][2];
};

#endif