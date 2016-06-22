/* 
COPYRIGHT NOTIFICATION

(C) COPYRIGHT 2004 UNIVERSITY OF CHICAGO

This program discloses material protectable under copyright laws of the United States.
Permission to copy and modify this software and its documentation is
hereby granted, provided that this notice is retained thereon and on all copies or
modifications. The University of Chicago makes no representations as to the suitability
and operability of this software for any purpose. It is provided "as is"; without
express or implied warranty. Permission is hereby granted to use, reproduce, prepare
derivative works, and to redistribute to others, so long as this original copyright notice
is retained.  

Any publication resulting from research that made use of this software 
should cite the document:  Steven J. Benson and Jorge Mor\'{e}, 
"A Limited-Memory Variable-Metric Algorithm for Bound-Constrained Minimization",
Mathematics and Computer Science Division, Argonne National Laboratory,
ANL/MCS-P909-0901, 2001.




    Argonne National Laboratory with facilities in the states of Illinois and Idaho, is
    owned by The United States Government, and operated by the University of Chicago under
    provision of a contract with the Department of Energy.

                                    DISCLAIMER
    THIS PROGRAM WAS PREPARED AS AN ACCOUNT OF WORK SPONSORED BY AN AGENCY OF THE UNITED
    STATES GOVERNMENT. NEITHER THE UNITED STATES GOVERNMENT NOR ANY AGENCY THEREOF, NOR THE
    UNIVERSITY OF CHICAGO, NOR ANY OF THEIR EMPLOYEES OR OFFICERS, MAKES ANY WARRANTY, EXPRESS
    OR IMPLIED, OR ASSUMES ANY LEGAL LIABILITY OR RESPONSIBILITY FOR THE ACCURACY,
    COMPLETENESS, OR USEFULNESS OF ANY INFORMATION, APPARATUS, PRODUCT, OR PROCESS DISCLOSED,
    OR REPRESENTS THAT ITS USE WOULD NOT INFRINGE PRIVATELY OWNED RIGHTS. REFERENCE HEREIN TO
    ANY SPECIFIC COMMERCIAL PRODUCT, PROCESS, OR SERVICE BY TRADE NAME, TRADEMARK,
    MANUFACTURER, OR OTHERWISE, DOES NOT NECESSARILY CONSTITUTE OR IMPLY ITS ENDORSEMENT,
    RECOMMENDATION, OR FAVORING BY THE UNITED STATES GOVERNMENT OR ANY AGENCY THEREOF. THE
    VIEW AND OPINIONS OF AUTHORS EXPRESSED HEREIN DO NOT NECESSARILY STATE OR REFLECT THOSE OF
    THE UNITED STATES GOVERNMENT OR ANY AGENCY THEREOF.
*/ 
/*
   Applications of the BLMVM solver for bound constrained minimization must 
   implement 2 routines: BLMVMFunctionGradient(), BLMVMConverge(). In addition, they must
   call the routine BLMVMSolveIt() with the number of variables, and initial solution,
   lower and upper bounds, and a parameter.  To solve applications other than the following example,
   replace the two routines with other routines and call BLMVMSolveIt() with the appropriate arguments.
*/

/*
 * $Id: blmvm.h,v 1.1.1.1 2007/01/25 09:01:39 y-matsu Exp $
 */

#ifndef __BLMVM_H_
#define __BLMVM_H_

struct  _P_BLMVMVec{
  int    dim;
  double *val;
};

typedef struct _P_BLMVMVec *BLMVMVec;

struct  _P_LMVMMat{

  int lm;
  int lmnow;
  int iter;
  int rejects;

  double eps;

  BLMVMVec *S;
  BLMVMVec *Y;
  BLMVMVec Gprev;
  BLMVMVec Xprev;

  double y0normsquared;
  double *rho;
  double *beta;
};

typedef struct  _P_LMVMMat *LMVMMat;

struct  P_BLMVM{

  LMVMMat  M;

  BLMVMVec DX;
  BLMVMVec GP;
  BLMVMVec G;
  BLMVMVec XL;
  BLMVMVec XU;
  BLMVMVec Xold;

  int pgits;

};

typedef struct  P_BLMVM *BLMVM;

#endif

/*
 * $Log: blmvm.h,v $
 * Revision 1.1.1.1  2007/01/25 09:01:39  y-matsu
 *
 *
 * Revision 1.1.1.1  2006/09/14 10:33:25  y-matsu
 *
 *
 * Revision 1.2  2005/04/27 10:30:44  tsuruoka
 * add copyright
 *
 * Revision 1.1  2004/07/26 13:10:55  tsuruoka
 * add files
 *
 * Revision 1.1  2004/07/02 09:15:36  tsuruoka
 * add LMVM
 *
 */

