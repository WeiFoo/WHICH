#ifndef _tool_h
#define _tool_h

#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <cmath>
#include <ctime>
#include <unistd.h>
#include <vector>
#include "defines.h"
#include "WhichStack.h"
#include "Rule.h"
#include "Data.h"

#define TotalMitigations 99 
#define RunTotal 100

struct Components
{
  float mCost;
  float mAtt;
};

float tool(Rule *rule);
float medianScore(float *medianCost, float* medianAtt);
void findDistanceSweetSpot(void);
int selectValue(int val1, int val2);
void addInstance(float costVar, float attVar);
float minValue(float val1, float val2);
void model(float *cost, float *att, float m[]);
void ruleToModel( Rule *r, float model[] );

#endif
