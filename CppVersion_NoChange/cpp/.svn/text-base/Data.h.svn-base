#ifndef _data_h_
#define _data_h_
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <map>

class Rule;

union InstanceElement
{
	int mIndex;
	float mValue;
};

struct ListItem
{
        float mVal;
	int mPos;

	ListItem(){}

	ListItem( float val, int pos )
	{
		mVal = val;
		mPos = pos;
	}

	bool operator<( const ListItem &li ) const
	{
		return mVal < li.mVal;
	}
};

/**
 * This class represents a data file.  It facilitates the structures necessary to easily
 * get infomormation from the data.
**/
class Data
{
	public:
		/**
		 * Empty Constructor.
		**/
		Data();

		/**
		 * Destructor.
		**/
		~Data();

		/**
		 * Reads in the training ARFF file and creates the Data instance.
		 * @param fName The name of the file to read in.
		 * @return The file stream.
		**/
		void read( std::string fName );

		/**
		 * This method will discretize the attributes that are continuous using
		 * an equal interval discretization method.
		 * @param bins The number of bins to use.
		 * @param combine Another data set to combine with this one in the discretization.
		**/
		void discretizeEqInt( int bins, Data *combine );

		/**
		 * This method will discretize the attribtues that are continous using
		 * an equal frequency discretization method.
		 * @param bins The number of bins to use.
		 * @param combine Another data set to combine with this one in the discretization. If this is null,
		 * this is ignored.
		**/
		void discretizeEqFreq( int bins, Data *combine = NULL );

		/**
		 * This method will subsample the data.  That is, remove instances of data that are not the
		 * desired class until the percentage of the desired class in the entire data set is met.
		 * @param desClass The index of the desired class.
		 * @param per The desired percent.  If this is smaller than the percent makeup already, this method
		 * does nothing.
		 * @return true if the set has been altered, false otherwise.
		**/
		bool subsample( unsigned int desClass, float per );

		/**
		 * This method will microsample that data.  This involves having an equal distribution of
		 * all classes and a total number of each class being equal to amount.
		 * @param amount The number of each class to be left in the data set.
		 * @return The actual number of each class left in the data set.  If amount > size( class ) than it will only remove from other classes.
		**/
		unsigned int microsample( unsigned int amount );
		
		/**
		 * This method will normalize an attribute so that each value is between 0 and 1 and the
		 * greatest attribute is equal to 1.
		 * @param attIndex The index of the attribute to normalize.
		 **/
		void normalizeAttribute( int attIndex );

		/**
		 * Creates a copy of the Data with the attributes and instance information.
		 * @return The copied Data.
		**/
		Data *clone();
		
		/**
		 * This method will remove all instances of data from the data set that are covered by
		 * a given rule.
		 * @param rule The rule to check coverage.
		 * @return true if the set was altered, false otherwise.
		**/
		bool cover( Rule *rule );

		/**
		 * Compares two ListItems.
		 * @param l1 The first ListItem.
		 * @param l2 The second Listitem.
		 * @return 0 if l1 = l2, -1 if l1 < l2, or 1 if l1 > l2.
		**/
		int compareListItems( ListItem l1, ListItem l2 );

		/**
		 * Calculates the base lift of the data.
		**/
		void calcLift();

		/**
		 * Calulates the base infomation needed for Effort scoring.
		 * @param LOC The attribue that is the lines of code.
		**/
		void calcPDPFEst( unsigned int LOC );
		
		/**
		 * Calculates the frequency counts of each attribute-value pair.
		 * Assumes all data is discrete.
		 * Assumes only 2 ordered classes.( Best is second class )
		**/
		void calcProbSupt();

		/**
		 * Gets the base lift of the data.
		 * @return The base lift.
		**/
		float getLift();

		/**
		 * Gets the total lines of code in this data instance.
		 @return The total lines of code.
		**/
		int getTotLOC();

		/**
		 * Gets the lines of code per instance.
		 * @return A vector containing the lines of code per instance.
		**/
		std::vector< int > getLOCs();

		/**
		 * Gets the instance set.
		 * @return The instance set.
		**/
		std::vector< std::vector< InstanceElement * > * > getInstanceSet();

		/**
		 * Gets the number of attributes.
		 * @return The number of attributes.
		**/
		unsigned int getNumAtts();

		/**
		 * Gets the number of class values.
		 * @return The number of class values.
		**/
		unsigned int getNumClasses();

		/**
		 * Gets the class index for a given instance.
		 * @param An instance of data.
		 * @return The class index.
		**/
		unsigned int getClassIndex( std::vector< InstanceElement * > *instance );

		/**
		 * Gets the number of values for a given attribute.
		 * @param att The attribute.
		 * @return the number of values for att.
		**/
		unsigned int getNumAttVals( std::string att );

		/**
		 * Gets the attribute name of the index'th attribute.
		 * @param index The name to return.
		 * @return The name of the attribute at index.
		**/
		std::string getAttName( int index );

		/**
		 * Gets the index of an attribute if the string sent in matches it.
		 * @param name The name of the attribute to find the index of.
		 * @return The index if found, number of attributes + 1 otherwise.
		 **/
		unsigned int getAttIndex( std::string name );		

		/**
		 * Gets the index of an attribute value if the string sent in matches it.
		 * @param attName The name of the attribute.
		 * @param valName The name of the attribute value to match.
		 * @return The index if found, number of attribute values + 1 otherwise.
		 **/
		unsigned int getAttValIndex( std::string attName, std::string valName );

		/**
		 * Gets the name of the attribute value at the index'th value.
		 * @param att The name of the attribute.
		 * @param index the value to get.
		 * @return The name of the attribute value at the index.
		**/
		std::string getAttValName( std::string att, int index );

		/**
		 * Gets the class name at the index'th location.
		 * @param index The index of the class to get.
		 * @return The class name in string form.
		**/
		std::string getClassName( int index );

		/**
		 * Gets the class frequency vector.
		 * @return The class frequency vector.
		**/
		std::vector< int > getClassFreqs();

		/**
		 * Gets the frequency count table for best^2/(best+rest)
		 * @return A jagged array with each 2-dimensinal access containing
		 * a length two array with the first element being the rest count and
		 * the second element being the best count of this attribute-value pair.
		**/
		const std::vector< std::vector< int * > > *getFrequencyTable();

		/**
		 * This method will print the attributes.
		**/
		void printAttributes();

		/**
		 * This method will print the data set.
		**/
		void printDataSet( std::ostream &stream );

		/**
		 * This method prints the class names and frequencies.
		**/
		void printClassDist();

		/**
		 * This method will print one instance of the data set.
		 * @param inst The instance number to print.
		**/
		void printInstance( int inst );

		/**
		 * This method will print all of the attribute value best and rest frequencies.
		 * @param stream The stream to print to.
		**/
		void printFrequencyTable( std::ostream &stream );
		
	protected:
		void processAttribute( std::string line );
		void processInstance( std::string line );
		std::string preprocessString( std::string line );
		int find( std::string att, std::vector< std::string > &l );

		std::string mFileName;
		std::string mClassName;
		std::vector< int > mClassFreqs;
		std::vector< std::vector< int * > > mAttrValFreqs;
		std::vector< std::string > mAtts;
		std::vector< bool > mIsReal;
		std::map< std::string, std::vector< std::string > > mAttVals;
		std::vector< std::vector< InstanceElement * > * > mInstances;
		std::vector< int > mLOCs;
		float mLift;
		int mTotLOC;
};

#endif
