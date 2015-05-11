
#ifndef _pickobject_h_
#define _pickobject_h_

#include <iostream>
#include <vector>

union InstanceElement;
class Data;

/**
 * Represents a set of disjunctions for a given attribute.
**/
struct DisjunctionSet
{
	int mAttribute;
	std::vector< int > mValues;
};

enum RULE_TYPE { LIFT, EFFORT, PROBSUPT, INFOGAIN, PDPF, PDOVEREFFORT, PDOVERLOC, RIPPER, PRECISION, SPECIAL };

/**
 * Represents a Rule for Which.  Contains a series of attributes and the ranges they can have for a rule to fire.
 * Rules in Which are a series of conjunctions of disjunctions.
 * EG: ( a = 3 + a = 2 )( b = 9 + b = 5 )( ... )
**/
class Rule
{
	public:
		/**
		 * Creates an empty Rule.  After this constructer the Rule will have no attributes to fire on.
		**/
		Rule();

		/**
		 * Creates a Rule with one conjunction.( if attribute = attributeValue then... )
		 * @param attribute The numerical index of the attribute in the data set.
		 * @param value The numerical index of the attribute's value in the data set.
		 * @param d A pointer to the data set to score this Rule with.
		 * @param type The type of Rule this is.
		 * @param the method to use to score this rule. Only needed for type = SPECIAL
		**/
		Rule( int attribute, int value, Data *d, RULE_TYPE type, float (*scoreFnc)( Rule * ) = NULL );

		/**
		 * Destructor.
		**/
		~Rule();

		void *getComponent();
		void setComponent( void *com );
		std::vector< DisjunctionSet * > *getRuleSet();

		void setData( Data *d );
		void setWeights( float alpha, float beta, float gamma );

			
		float getScore();
		float getSupport();
		float getPD();
		float getPF();
		float getEffort();
		int getSize();

		/**
		 * Creates a cloned version of this Rule.  The new Rule is completely seperate of this Rule.
		 * @return The newly cloned Rule.
		**/
		Rule *clone();

		/**
		 * Creates a Rule from reading in a file.
		 * @param fName The name of the file.
		 * @param Data The data set to score and create this Rule with.
		 * @param type The type of Rule this is.
		 * @param the method to use to score this rule. Only needed for type = SPECIAL
		 * Returns false if no Rule was created.  True otherwise.
		 **/
		bool createFromFile( std::string fName, Data *d, RULE_TYPE type, float (*scoreFcn)( Rule * ) = NULL );

		/**
		 * Compares two Rules' scores.
		 * @param r The Rule to compare to this one.
		 * @returns >0 if r is greater than this Rule, 0 if r is equal to this Rule, <0 if r is less than this Rule.
		**/
		float compare( Rule *r );

		/**
		 * Checks to see if an instance of data is satisfied by this Rule.
		 * @param instance The instance of data.
		**/
		bool isSatisfied( std::vector< InstanceElement * > *instance );

		/**
		 * Scores the Rule based on which type of Rule it is.
		**/
		void score(bool isTest = false);

		/**
		 * Checks to see if an attribute index is already in the Rule.
		 * @param attribute The attribute index to search for.
		 * @return -1 if the attribute does not exist, the index of the attribute otherwise.
		**/
		int findAttribute( int attribute );

		/**
		 * Checks to see if an attribute value is already in the Rule.
		 * @param attribute The attribute whose value is to be searched for.
		 * @param value The value of the attribute to search.
		 * @return -1 if the value is not found, the index of the value otherwise.
		**/
		int findAttributeValue( int attribute, int value );

		/**
		 * Checks to see if a certain attribute value is in the Rule.
		 * @param attribute The attribute index to check the value of.
		 * @param value The value index of the attribute.
		 * @return True if it attribute = value is in this Rule, false otherwise.
		**/
		bool hasComponent( int attribute, int value );

		/**
		 * Checks to see if two Rules have the same component sets.
		 * @param r The Rule to compare to this one.
		 * @return True if r == this, false otherwise.
		**/
		bool isEqualTo( Rule *r );

		/**
		 * Adds a new component to the Rule.
		 * @param atribute The attribute to add.
		 * @param vale The value of the attribute to add.
		 * @return True if it was added, false if it already was in the rule.
		**/
		bool addComponent( int attribute, int value );

		/**
		 * Combines two Rules by adding together their disjunctions and conjunctions.  If this Rule and r are
		 * equivalent, the new Rule is just a clone of the first rule.
		 * @param r The Rule to add to this one.
		 * @return A pointer to a new Rule that is created from this one.
		**/
		Rule *combine( Rule *r );

		/**
		 * Attempts to create a better, smaller rule.
		 * @return The smaller rule.
		**/
		Rule *backSelect();

		/**
		 * Prints a Weka-like got want matrix to allow for evaluation alongside the Weka.
		 * @param stream The stream to print o.
		 * @param eData The data containing the proper line of code information.
		**/
		void printGotWant( std::ostream& stream, Data *eData );

		/**
		 * Prints the Rule in the format:
		 * A =		[ 1 OR 2 ]
		 * AND B =	[ 2 ]
		 * AND C =	[ 1 OR 4 ]
		 * Score:	###
		 * <optional scoring metrics>
		 * @param stream The stream to print the Rule to.
		**/
		void print( std::ostream& stream );

		/**
		 * Prints just the Rule portion in the format.
		 * A = [ 1 OR 2 ] AND B = [ 2 ] AND C = [ 1 OR 4 ] => class
		 * @param stream The stream to print tte Rule to.
		**/
		void printRule( std::ostream& stream ); 

	protected:
		void scoreLift();
		float calcDist();
		void scoreEffort(bool isTest = false);
		void scoreProbSupt();
		void scoreInfoGain();
		void scorePDPF();
		void scorePDOverEffort();
		void scorePDOverLOC();
		void scoreRipper();
		void scorePrecision();
		void scoreSpecial();

		Data *mData;
		std::vector< DisjunctionSet * > mPicked;
		float mScore;
		int mSize, mTargetClass;
		float mPD, mPF, mEffort, mAlpha, mBeta, mGamma, mProbBest, mProbRest;
		float mSupport;
		RULE_TYPE mType;
		float (*mScoreFcn)( Rule * );
		void *mComponent;
};

#endif
