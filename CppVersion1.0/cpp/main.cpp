#include "Data.h"
#include "Rule.h"
#include "RuleSet.h"
#include "WhichStack.h"
#include "defines.h"
#include <sstream>
#include <ctime>
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cmath>
using namespace std;

/**
 * Prints help information for Which.
**/
void printHelp( string comStr );

int main( int argc, char **argv )
{
	time_t t = time(NULL);
	string files[3] = { "none", "none", "none" }, tarFile;
	int locAtt = 0, 
	  stackSize = INFINITY, 
	  picks = 2000,
	  check = 200,
	  reportNo = 1,
	  discBins = 4,
	  scoreType = LIFT,
	  microAmt = 0;
	float improvement = 0.2, alpha = 1, beta = 1000, gamma = 0, seed = time(NULL);
//    ofstream writeTo("/Users/WeiFu/Github/WHICH/CppVersion1.0/cpp/Rule111.csv", ios_base::trunc);
	bool statOnly = false, wekaP = false, noeff = false, justRule = false, isTar3 = false;

	/*
	Data *train = new Data(), *test = new Data(), *effort = new Data();
	WhichStack *stack = new WhichStack( INFINITY );
	train->read( "fakc3_mod.arff" );
	test->read( "fakc3_mod.arff" );
	effort->read( "mdp/kc3_mod.arff" );
	effort->calcPDPFEst( 38 );
	stack->create( train, PDPF, 1, 1000, 0 );
	stack->select();
	stack->getBest()->setData( test );
	stack->getBest()->score();
	stack->getBest()->printGotWant( cout, effort );
	*/

	// Parse the command-line arguments.
	for ( int command = 1; command < argc; command += 2 )
	{
	  string comStr = argv[command], dumb;
	  stringstream ss( stringstream::in | stringstream::out );
	  ss << argv[command+1] << endl;
	  if ( comStr == "-t" ) ss >> files[0];
	  else if ( comStr == "-T" ) ss >> files[1];
	  else if ( comStr == "-E" ) ss >> files[2];
	  else if ( comStr == "-rep" ) ss >> reportNo;
	  else if ( comStr == "-score" )
	  {
	    string type;
	    ss >> type;
	    if ( type == "lift" ) scoreType = LIFT;
	    else if ( type == "effort" ) scoreType = EFFORT;
	    else if ( type == "pdpf" ) scoreType = PDPF;
	    else if (type == "probsupt" ) scoreType = PROBSUPT;
	    else if ( type == "pd/effort" ) scoreType = PDOVEREFFORT;
	    else if ( type == "pd/loc" ) scoreType = PDOVERLOC;
	    else if ( type == "ripper" ) scoreType = RIPPER;
	    else if ( type == "precision" ) scoreType = PRECISION;
	  }
	  else if ( comStr == "-ssize" ) ss >> stackSize;
	  else if ( comStr == "-imp" ) ss >> improvement;
	  else if ( comStr == "-picks" ) ss >> picks;
	  else if ( comStr == "-check" ) ss >> check;
	  else if ( comStr == "-loc" ) { ss >> locAtt; locAtt--; }
	  else if ( comStr == "-bins" ) ss >> discBins;
	  else if ( comStr == "-alpha" ) ss >> alpha;
	  else if ( comStr == "-beta" ) ss >> beta;
	  else if ( comStr == "-gamma" ) ss >> gamma;
	  else if ( comStr == "-micro" ) ss >> microAmt;
	  else if ( comStr == "-stat" ) { ss >> dumb; statOnly = true; command--; }
	  else if ( comStr == "-noeff" ) { ss >> dumb; noeff = true; command--; }
	  else if ( comStr == "-rule" ) { ss >> dumb; justRule = true; command--; }
	  else if ( comStr == "-seed" ) ss >> seed;
	  else if ( comStr == "-p" ) { ss >> dumb; wekaP = true; command--; }
	  else if ( comStr == "-tar3" ) { ss >> tarFile; isTar3 = true; }
	  else printHelp( comStr );
	}

	// Set up the data according to the read in arguments.
	srand( seed );
	Data *train = new Data(), *test = new Data(), *effort = new Data();
	train->read( files[0] );
	if ( files[1] == "none" ) files[1] = files[0];
	test->read( files[1] );
	
	if ( microAmt > 0 ) train->microsample( microAmt );

	if ( !noeff )
	{
	  train->calcPDPFEst( locAtt );
	  test->calcPDPFEst( locAtt );
	}
	
	if ( scoreType == PDOVERLOC ) 
	{
	  train->normalizeAttribute( locAtt );
	  test->normalizeAttribute( locAtt );
	}

	train->discretizeEqFreq( discBins, test );
	train->calcLift();
	test->calcLift();
	train->calcProbSupt();
	test->calcProbSupt();

	if ( isTar3 )
	{
	  Rule *tarRule = new Rule();
	  tarRule->createFromFile( tarFile, test, LIFT );
	  tarRule->print( cout );
	}

	// Create and setup the WhichStack
	WhichStack *stack = new WhichStack( stackSize );
	stack->create( train, scoreType, alpha, beta, gamma );
	stack->select( picks, check, improvement );

	if ( !statOnly && !wekaP )
	{
	  for ( int r = 0; r < reportNo; r++ )
	  {
	    stack->getRule( r )->setData( test );
	    stack->getRule( r )->score(true);
	    if ( justRule ) stack->getRule( r )->printRule( cout );
	    else stack->getRule( r )->print( cout );
	    cout << endl;
	  }
	  
	  float hours = (time(NULL)-t)/3600.0;
	  float minutes = (hours-floor(hours))*60;
	  float seconds = (minutes-floor(minutes))*60;
	  cout << "It took " << floor(hours) << " hour(s), " << floor(minutes) << " minute(s), and " << seconds << " second(s) to run." << endl;
	}
	else if ( statOnly )
	{
	  for ( int r = 0; r < reportNo; r++ )
	  {
	    stack->getRule( r )->setData( test );
	    stack->getRule( r )->score();
	    cout << stack->getRule( r )->getPD() << "," << stack->getRule( r )->getPF() << endl;
	  }
	  cout << endl;
	}
	else if ( wekaP )
	{
	  stack->getBest()->setData( test );
	  stack->getBest()->score();
	  stack->getBest()->printGotWant( cout, test );
	  cout << endl;
	}

	return 0;
}

void printHelp( string comStr )
{
  if ( comStr != "-?" )
	cout << comStr << " is not a valid option." << endl << endl;

  cout << "Usage:" << endl;
  cout << "./which [options]" << endl;
  cout << "[options]" << endl;
  cout << "\t-t\t\t" << "Sets the train file." << endl;
  cout << "\t-T\t\t" << "Sets the test file." << endl;
  cout << "\t-E\t\t" << "Sets the file to read in the lines of code from" << endl;
  cout << "\t-rep\t\t" << "Sets the number of Rules to report." << endl;
  cout << "\t-score\t\t" << "Sets the type of scoring" << endl;
  cout << "\t\t\t\t" << "lift -" << "Scores the Rules via lift." << endl;
  cout << "\t\t\t\t" << "effort -" << "Scores the Rules via effort." << endl;
  cout << "\t\t\t\t" << "pdpf -" << "Scores the Rules via probability of detection and probability of false alarm." << endl;
  cout << "\t\t\t\t" << "probsupt -" << "Scores the Rules via the equation pd^2/(pd+pf)." << endl;
  cout << "\t\t\t\t" << "pd/effort -" << "Scores the Rules via pd/effort." << endl;
  cout << "\t\t\t\t" << "ripper -" << "Scores the Rules via Ripper's method according to ROC n' Rule paper." << endl;;
  cout << "\t\t\t\t" << "precision -" << "Scores the Rules via precision's method according to ROC n' Rule paper." << endl;;
  cout << "\t\t\t\t" << "pd/loc -" << "Scores the Rules via pd over the sum of the LOC it fires on.  LOCs are normalized for this." << endl;
  cout << "\t-ssize\t\t" << "Sets the size of the stack( -1 for infinite size." << endl;
  cout << "\t-imp\t\t" << "Sets the minimum improvement required per -check picks. Stopping criteria." << endl;
  cout << "\t-picks\t\t" << "Sets the max number of picks for this run of Which." << endl;
  cout << "\t-check\t\t" << "Sets how many picks in a row before a -imp case is checked." << endl;
  cout << "\t-loc\t\t" << "If scoring type is effort, this is the location in the file of the line-of-code attribute." << endl;
  cout << "\t-bins\t\t" << "How many bins to use to discretize the data." << endl;
  cout << "\t-alpha\t\t" << "Sets the weight of PD in all scoring methods that use it." << endl;
  cout << "\t-beta\t\t" << "Sets the weight of PF in all scoring methods that use it." << endl;
  cout << "\t-gamma\t\t" << "Sets the weight of effort in all scoring methods that use it." << endl;
  cout << "\t-micro\t\t" << "Creates a data set of even distribution of classes from the train set and removes all but the amount sent in." << endl;
  cout << "\t-stat\t\t" << "Output only the stats of each rule." << endl;
  cout << "\t-p\t\t" << "Tells Which to print the got want table." << endl;
  cout << "\t-noeff\t\t" << "Tells which to ignore effort calculation." << endl;
  cout << "\t-rule\t\t" << "Tells which to only print the Rule in a condensed format." << endl;
  cout << "\t-seed\t\t" << "Tells which which seed to use for the random number generator." << endl;
  cout << "\t-tar3\t\t" << "Tells which to read in a file and score it." << endl;
  cout << "\t-?\t\t" << "Prints this help file." << endl << endl;

  exit( 0 );
}
