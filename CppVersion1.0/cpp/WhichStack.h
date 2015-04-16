#ifndef _whichstack_h_
#define _whichstack_h_

#include <vector>
#include <iostream>
class Rule;
class Data;
//enum RULE_TYPE;

/**
 * Represents a Which-specific stack.  It is sorted and has special facilities geared towards Which.
**/
class WhichStack
{
		public:
		/**
		 * Empty Constructor.
		**/
		WhichStack();

		/**
		 * Creates a WhichStack that has a maximum size.
		 * @param maxSize The maximum size this WhichStack can be.  If it is -1, the size if infinite.
		**/
		WhichStack( int maxSize );

		/**
		 * Destructor.
		**/
		~WhichStack();

		/**
		 * Creates a WhichStack having Rules of single attribute-value pairs.
		 * @param data The data file to use to create the Rules from.
		 * @param type The type of Rules to create.
		 * @param alpha The weight for pd.
		 * @param beta The weight of pf.
		 * @param gamma The weight for effort.
		**/
		void create( Data *data, int type, float alpha = 1, float beta = 1, float gamma = 1 );

		/**
		 * Pushes a Rule onto the WhichStack in the position based on the Rule's score.
		 * If the Rule would be last on a WhichStack of finite size that is full, the item
		 * will not be pushed.
		 * --- THE RULE WILL NOT BE DELETED IF IT IS NOT ADDED ---
		 * @param r The Rule to push onto the WhichStack.
		 * @return True if the Rule made it onto the WhichStack, false otherwise.
		**/
		bool push( Rule *r );

		/**
		 * Calls pickTwo a series of times to attempt to create a "best" Rules.
		 * @param count The number of times to call PickTwo total.
		 * @param check How many pickTwo calls to allow to pass
		 * before a check is made to make sure improvement is still happening.
		 * @param improve A decimal number representing the percentage of increase
		 * in score a current "best" Rule must have since the last check
		 * in order to continue calling pickTwo.
		 * @return The true number of times pickTwo was called.  A number <= count.
		**/
		int select( int count = 2000, int check = 200, float improve = 0.2 );

		/**
		 * Based on a weighted distribution, picks two Rules from the WhichStack and combines them.
		 * @return True if the new Rule made it onto the WhichStack, false otherwise.
		**/
		bool pickTwo();

		/**
		 * Gets the number of Rules in the WhichStack.
		 * @return The number of Rules in the WhichStack.
		**/
		unsigned int size();

		/**
		 * Gets the best Rule in the WhichStack.
		 * @return The top of the WhichStack.
		**/
		Rule *getBest();

		/**
		 * Gets the Rule indexed by index.
		 * @param index The index of the Rule to get( 0 is the same as calling getBest() );
		 * @return The Rule at index index.
		**/
		Rule *getRule( int index );

		/**
		 * Prints the first n Rules in the WhichStack.
		 * @param stream The stream to print to.
		 * @param n The number of Rules to print.
		 * @return The stream;
		**/
		std::ostream &report( std::ostream &stream, int n );

		/**
		 * Outputs the WhichStack to a stream.
		 * @param stream The stream to output to.
		**/
		void print( std::ostream& stream );

		bool push( int[], float (*scoreFcn)( Rule * ) );

	protected:
		/**
		 * Checks to see if a Rule is already in this WhichStack.
		 * @param r The Rulet to look for.
		 * @return True if r is in this WhichStack, false otherwise.
		**/
		bool contains( Rule *r );

		/**
		 * Picks a Rule from the WhichStack.
		 * @param scores The vector of scores for the rule.
		 * @param max The maximum number to select.
		 * @return The position in the WhichStack of the chosen rule.
		**/
		int pick( std::vector< float > scores, float sum );

		std::vector< Rule * > mRules;
		int mMaxSize;
};

#endif
