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
 * $Id: blmvm.cpp,v 1.2 2008/05/16 11:37:50 matuzaki Exp $
 */

/*
 * this file is a slightly modified version of blmvm.c by Steven J. Benson
 * obtained from  http://www-unix.mcs.anl.gov/~benson/blmvm/
 */
  
#include <cmath>
#include <cfloat>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <cstring>

#include "blmvm.h"
#include "maxent.h"


#define min(a,b) ((a <= b)? (a) : (b))
#define max(a,b) ((a >= b)? (a) : (b))

static int BLMVMVecCreateSeq(int,BLMVMVec*);
static int BLMVMVecCreateWArray(BLMVMVec*,double*,int);
static int BLMVMVecDuplicate(BLMVMVec,BLMVMVec*);
static int BLMVMVecSet(double,BLMVMVec);
static int BLMVMVecCopy(BLMVMVec,BLMVMVec);
static int BLMVMVecAXPY(double,BLMVMVec,BLMVMVec);
static int BLMVMVecAYPX(double,BLMVMVec,BLMVMVec);
static int BLMVMVecWAXPY(double,BLMVMVec,BLMVMVec,BLMVMVec);
static int BLMVMVecPointwiseMin(BLMVMVec,BLMVMVec,BLMVMVec);
static int BLMVMVecPointwiseMax(BLMVMVec,BLMVMVec,BLMVMVec);
static int BLMVMVecDot(BLMVMVec,BLMVMVec,double*);
static int BLMVMVecDestroy(BLMVMVec*);
static int BLMVMVecScale(double,BLMVMVec);
static int BLMVMVecProjectGradient(BLMVMVec,BLMVMVec,BLMVMVec,BLMVMVec,BLMVMVec);

static int LMVMMatCreate(int,BLMVMVec,LMVMMat*);
static int LMVMMatUpdate(LMVMMat,BLMVMVec,BLMVMVec);
static int LMVMMatSolve(LMVMMat,BLMVMVec,BLMVMVec);
static int LMVMMatDestroy(LMVMMat);


#define __FUNCT__ "Function Unknown"

#ifndef CHKERRQ
#define CHKERRQ(a)  { if (a){ printf(__FUNCT__); return a; } }
#endif

//int BLMVMFunctionGradient(double*,double*,double*,int);
//int BLMVMLowerAndUpperBounds(double*,double*,int);
/* ---------------------------------------------------------- */
#undef __FUNCT__  
#define __FUNCT__ "BLMVMComputeFunctionGradient"
int
ME_Model::BLMVMComputeFunctionGradient(BLMVM blmvm, BLMVMVec X,double *f,BLMVMVec G){
  int info;
  double *x=X->val,*g=G->val;
  info=BLMVMFunctionGradient(x,f,g,G->dim);CHKERRQ(info);
  return (0);
}

#undef __FUNCT__  
#define __FUNCT__ "BLMVMComputeBounds"
int
ME_Model::BLMVMComputeBounds(BLMVM blmvm, BLMVMVec XL, BLMVMVec XU){
  int info;
  double *xl=XL->val,*xu=XU->val;
  info=BLMVMLowerAndUpperBounds(xl,xu,XL->dim);
  return (0);
}

#undef __FUNCT__  
#define __FUNCT__ "Solve_BLMVM"
int
ME_Model::Solve_BLMVM(BLMVM blmvm, BLMVMVec X){

  BLMVMVec  Xold=blmvm->Xold,G=blmvm->G,GP=blmvm->GP;
  BLMVMVec  DX=blmvm->DX;
  BLMVMVec  XL=blmvm->XL,XU=blmvm->XU;
  LMVMMat   M=blmvm->M;
  int       info,iter=0,ffeval=1,lscount;
  double    gnorm2,alpha=0,gdx;
  //  double    gtol=0.001;
  double    gtol=0.0001;
  double    f,fnew;

  info=BLMVMComputeBounds(blmvm,XL,XU); CHKERRQ(info);
  info=BLMVMVecPointwiseMin(X,XU,X); CHKERRQ(info);
  info=BLMVMVecPointwiseMax(X,XL,X); CHKERRQ(info);
  info = BLMVMComputeFunctionGradient(blmvm,X,&f,G); CHKERRQ(info);
  blmvm->pgits=0;

  while (1){
    info=BLMVMVecProjectGradient(XL,X,XU,G,GP); CHKERRQ(info);
    info=BLMVMVecDot(GP,GP,&gnorm2); CHKERRQ(info);

    //    printf("Iter: %d, F: %4.4e,  pgnorm: %4.4e, step:%4.4e\n",iter,f,sqrt(gnorm2),-alpha);
    //    fprintf(stderr, "iter = %2d  f = %10.7f  train_err = %7.5f", iter, -f, _train_error);
    fprintf(stderr, "%3d  logl(err) = %10.7f (%7.5f)", iter, -f, _train_error);
    if (_heldout.size() > 0) {
      double hlogl = heldout_likelihood();
      fprintf(stderr, "  heldout_logl(err) = %f (%6.4f)\n", hlogl, _heldout_error);

      _vhlogl.push_back(hlogl);
      if (_early_stopping_n > 0) {
        if (_vhlogl.size() > _early_stopping_n) {
          double h0 = 0, h1 = 0;
          for (int i = 0; i < _early_stopping_n; i++) {
            h0 += _vhlogl[_vhlogl.size() - i - 2];
            h1 += _vhlogl[_vhlogl.size() - i - 1];
          }
          //          fprintf(stderr, "h0 = %f, h1 = %f\n", h0, h1);
          if (h1 < h0) {
            fprintf(stderr, "early stopping\n");
            info=BLMVMVecCopy(Xold, X);CHKERRQ(info);
            break;
          }
        }
      }
    } else {
      fprintf(stderr, "\n");
    }

    /* STOPPING CRITERIA -- THIS CAN BE MODIFIED */
    if (sqrt(gnorm2)<gtol || iter > 1000 || ffeval>10000) break;
    iter++;

    info=LMVMMatUpdate(M,X,GP); CHKERRQ(info);
    info=LMVMMatSolve(M,G,DX); CHKERRQ(info);
    info=BLMVMVecProjectGradient(XL,X,XU,DX,DX); CHKERRQ(info);

    info=BLMVMVecDot(G,DX,&gdx);CHKERRQ(info);
    if (gdx<=0){
      info=BLMVMVecCopy(GP,DX);CHKERRQ(info);
      blmvm->pgits++;
    }

    fnew=f;alpha=-1.0;lscount=0;
    info=BLMVMVecCopy(X,Xold);CHKERRQ(info);
    while (fnew>=f){
      info=BLMVMVecWAXPY(alpha,DX,Xold,X);
      info=BLMVMVecPointwiseMin(X,XU,X); CHKERRQ(info);
      info=BLMVMVecPointwiseMax(X,XL,X); CHKERRQ(info);
      info=BLMVMComputeFunctionGradient(blmvm,X,&fnew,G); CHKERRQ(info);
      ffeval++;lscount++;
      if (fnew>=f) alpha=alpha*0.75;
      if (lscount>100) break;
    }
    f=fnew;
  }
  return(0);
}


#undef __FUNCT__  
#define __FUNCT__ "SetUp_BLMVM"
static int SetUp_BLMVM(BLMVM blmvm, BLMVMVec X, int lm){
  int info;
  info=BLMVMVecDuplicate(X,&blmvm->Xold); CHKERRQ(info);
  info=BLMVMVecDuplicate(X,&blmvm->DX); CHKERRQ(info);
  info=BLMVMVecDuplicate(X,&blmvm->GP); CHKERRQ(info);
  info=BLMVMVecDuplicate(X,&blmvm->G); CHKERRQ(info);
  info=BLMVMVecDuplicate(X,&blmvm->XL); CHKERRQ(info);
  info=BLMVMVecDuplicate(X,&blmvm->XU); CHKERRQ(info);  
  info=LMVMMatCreate(lm,X,&blmvm->M);CHKERRQ(info);
  return(0);
}

/* ---------------------------------------------------------- */
#undef __FUNCT__  
#define __FUNCT__ "SetDown_BLMVM"
static int SetDown_BLMVM(BLMVM blmvm){
  int info;
  info=BLMVMVecDestroy(&blmvm->Xold);CHKERRQ(info);
  info=BLMVMVecDestroy(&blmvm->DX);CHKERRQ(info);
  info=BLMVMVecDestroy(&blmvm->GP);CHKERRQ(info);
  info=BLMVMVecDestroy(&blmvm->G);CHKERRQ(info);
  info=BLMVMVecDestroy(&blmvm->XL);CHKERRQ(info);
  info=BLMVMVecDestroy(&blmvm->XU);CHKERRQ(info);
  info=LMVMMatDestroy(blmvm->M);CHKERRQ(info);
  return(0);
}

/*------------------------------------------------------------*/
int
ME_Model::BLMVMSolve(double *x, int n){
  int info,lm=8;
  BLMVM blmvm;
  BLMVMVec X;

  /* THE INTEGER PARAMETER lm CAN BE MODIFIED */
  blmvm=(BLMVM)malloc(sizeof(struct P_BLMVM));
  info=BLMVMVecCreateWArray(&X,x,n); CHKERRQ(info);
  info=SetUp_BLMVM(blmvm,X,lm); CHKERRQ(info);
  info=Solve_BLMVM(blmvm, X); CHKERRQ(info);
  info=SetDown_BLMVM(blmvm); CHKERRQ(info);
  free(blmvm);
  return(0);
}



/* THE FOLLOWING CODE IMPLEMENTS APPROXIMATE HESSIAN INVERSE MATRIX */
/* ---------------------------------------------------------- */
static int LMVMMatCreate(int nlm, BLMVMVec X, LMVMMat *MM){
  int i,info;
  LMVMMat M;
  M=(LMVMMat)malloc(sizeof(struct _P_LMVMMat));
  *MM=M;

  M->S=(BLMVMVec*)malloc((nlm+1)*sizeof(BLMVMVec));
  M->Y=(BLMVMVec*)malloc((nlm+1)*sizeof(BLMVMVec));

  M->rho=(double*)malloc((nlm+1)*sizeof(double));
  M->beta=(double*)malloc((nlm+1)*sizeof(double));
  
  M->lm=nlm;
  M->lmnow=0;
  M->eps=2.2e-16;
  M->eps=2.2e-11;
  M->iter=0;
  M->rejects=0;

  for (i=0;i<nlm+1;i++){
    info=BLMVMVecDuplicate(X,&M->S[i]); CHKERRQ(info);
    info=BLMVMVecDuplicate(X,&M->Y[i]); CHKERRQ(info);
  }
  M->Gprev=0;
  M->Xprev=0;
  return(0);
}

#undef __FUNCT__
#define __FUNCT__ "LMVMMatUpdate"
static int LMVMMatUpdate(LMVMMat M, BLMVMVec  X, BLMVMVec G){
  int i,info;
  int lm=M->lm,lmnow=M->lmnow;
  double rhotemp,rhotol;
  double y0temp;
  double   *rho=M->rho;
  BLMVMVec *Y=M->Y;
  BLMVMVec *S=M->S;
  BLMVMVec Gprev=M->Gprev;
  BLMVMVec Xprev=M->Xprev;

  if (M->Gprev==0 || M->Xprev==0){
    
    M->Gprev=M->Y[lm];
    M->Xprev=M->S[lm];
    M->rho[0]=1.0;
    M->y0normsquared = 1.0;
    M->iter=0;
    M->rejects=0;

  } else {
    
    M->iter++;
    info=BLMVMVecAYPX(-1.0,G,Gprev);CHKERRQ(info);
    info=BLMVMVecAYPX(-1.0,X,Xprev);CHKERRQ(info);
    info=BLMVMVecDot(Xprev,Gprev,&rhotemp);CHKERRQ(info);
    info=BLMVMVecDot(Gprev,Gprev,&y0temp);CHKERRQ(info);

    rhotol=M->eps*y0temp;
    if (rhotemp > rhotol){
      M->lmnow = min(lmnow+1,lm);
      for (i=lm-1;i>=0;i--){
        S[i+1]=S[i];
        Y[i+1]=Y[i];
        rho[i+1]=rho[i];
      }
      S[0]=M->Xprev;
      Y[0]=M->Gprev;
      rho[0]=1.0/rhotemp;
      M->y0normsquared=y0temp;
      M->Xprev=S[lm]; M->Gprev=Y[lm];

    } else { 
      M->rejects++;
    }
  }
  info=BLMVMVecCopy(X,M->Xprev);CHKERRQ(info);
  info=BLMVMVecCopy(G,M->Gprev);CHKERRQ(info);
  return (0);
}

#undef __FUNCT__
#define __FUNCT__ "LMVMMatSolve"
static int LMVMMatSolve(LMVMMat M, BLMVMVec G, BLMVMVec DX){

  int      ll,info;
  double   sq, yq;
  double   *rho=M->rho,*beta=M->beta;
  BLMVMVec *Y=M->Y;
  BLMVMVec *S=M->S;

  if (M->lmnow<1){rho[0]=1.0; M->y0normsquared = 1.0;}

  info=BLMVMVecCopy(G,DX);CHKERRQ(info);  
  for (ll = 0; ll<M->lmnow; ll++){
    info=BLMVMVecDot(DX,S[ll],&sq);CHKERRQ(info);
    beta[ll] = sq*rho[ll];
    info=BLMVMVecAXPY(-beta[ll], Y[ll],DX);CHKERRQ(info);
  }
  info=BLMVMVecScale(1.0/(rho[0]*M->y0normsquared),DX);CHKERRQ(info);
  for (ll=M->lmnow-1; ll>=0; ll--){
    info=BLMVMVecDot(DX,Y[ll],&yq);CHKERRQ(info);
    info=BLMVMVecAXPY(beta[ll]-yq*rho[ll],S[ll],DX);CHKERRQ(info);
  }
  return (0);
}

static int LMVMMatDestroy(LMVMMat M){
  int i,info;
  for (i=0;i<M->lm+1;i++){
    info = BLMVMVecDestroy(&M->S[i]); CHKERRQ(info);
    info = BLMVMVecDestroy(&M->Y[i]); CHKERRQ(info);
  }
  free(M->S);
  free(M->Y);
  free(M->rho);
  free(M->beta);
  free(M);
  return (0);
}


/* THE FOLLOWING CODE IMPLEMENTS VECTOR OPERATIONS */
/* ---------------------------------------------------------- */

static int BLMVMVecCreateSeq(int n ,BLMVMVec *VV){
  BLMVMVec V;
  V=(BLMVMVec)malloc(sizeof(struct _P_BLMVMVec));
  V->dim=n;
  *VV=V;
  if (n>0){
    V->val=(double*)malloc(n*sizeof(double));
    if (V->val==0) return 1;
  } else {
    V->val=0;
  }
  return 0;
}

static int BLMVMVecCreateWArray(BLMVMVec *VV, double* vv, int n){
  BLMVMVec V;
  V=(BLMVMVec)malloc(sizeof(struct _P_BLMVMVec));
  V->dim=n;
  *VV=V;
  if (n>0){
    V->val=vv;
  } else {
    V->val=0;
  }
  return 0;
}

static int BLMVMVecDestroy(BLMVMVec *V){
  if ((*V)->val){ free((*V)->val); }
  free(*V);
  return 0;
}

static int BLMVMVecCopy( BLMVMVec v1,  BLMVMVec v2){

  int n=v1->dim;
  double *val1=v1->val,*val2=v2->val;
  memcpy(val2,val1,n*sizeof(double));
  return 0;
}

static int BLMVMVecScale(double alpha, BLMVMVec x){
  int i,n=x->dim;
  double *xx=x->val;
  for (i=0; i<n; ++i){ xx[i]*= alpha;}
  return 0;
}

static int BLMVMVecAXPY(double alpha,  BLMVMVec x,  BLMVMVec y){
  int i,n=x->dim;
  double *yy=y->val,*xx=x->val;
  for (i=0; i<n; ++i){ yy[i] += (alpha)*xx[i];}
  return 0;
}

static int BLMVMVecWAXPY(double alpha, BLMVMVec x, BLMVMVec y, BLMVMVec w){
  int i,n=x->dim;
  double *yy=y->val,*xx=x->val,*ww=w->val;
  for (i=0; i<n; i++){ ww[i] = yy[i]+(alpha)*xx[i]; }
  return 0;
}


int BLMVMVecView(BLMVMVec V){
  int i,n=V->dim;
  double *vv=V->val;
  for (i=0; i<n; ++i){printf("%4.4e ",vv[i]);} printf("\n");  
  return 0;
}

static int BLMVMVecAYPX(double alpha,  BLMVMVec x,  BLMVMVec y){
  int i,n=x->dim;
  double *yy=y->val,*xx=x->val;
  for (i=0; i<n; ++i){ yy[i]=xx[i]+(alpha)*yy[i]; }
  return 0;
}

static int BLMVMVecDuplicate(BLMVMVec V1,BLMVMVec *V2){
  int info,n=V1->dim;
  info = BLMVMVecCreateSeq(n ,V2);CHKERRQ(info);
  return 0;
}

static int BLMVMVecSet(double alpha, BLMVMVec V){
  int i,n=V->dim;
  double *val=V->val;
  if (alpha==0.0){memset((void*)val,0,n*sizeof(double)); return 0; }
  for (i=0; i<n; ++i){ val[i]= alpha; }
  return 0;
}

static int BLMVMVecDot(BLMVMVec V1, BLMVMVec V2, double *ans){
  int i,m=V1->dim;
  double *v1=V1->val,*v2=V2->val;
  *ans=0.0;
  for (i=0; i<m; ++i){ *ans += v1[i]*v2[i]; }
  return 0;
}

static int BLMVMVecPointwiseMin( BLMVMVec V1, BLMVMVec V2, BLMVMVec V3){
  int i,n=V1->dim;
  double *v1=V1->val,*v2=V2->val,*v3=V3->val;
  for (i=0; i<n; ++i){ v3[i]=min(v2[i],v1[i]); }
  return 0;
}

static int BLMVMVecPointwiseMax( BLMVMVec V1, BLMVMVec V2, BLMVMVec V3){  
  int i,n=V1->dim;
  double *v1=V1->val,*v2=V2->val,*v3=V3->val;
  for (i=0; i<n; ++i){  v3[i]=max(v2[i],v1[i]); }
  return 0;
}

static int BLMVMVecProjectGradient( BLMVMVec XL, BLMVMVec X, BLMVMVec XU, BLMVMVec G, BLMVMVec GP){  
  int i,n=X->dim;
  double *x=X->val,*xl=XL->val,*xu=XU->val,*g=G->val,*gp=GP->val;
  for (i=0; i<n; i++){ 
    gp[i] = g[i];
    if (gp[i]>0 && x[i]<=xl[i]){
      gp[i] = 0;
    } else if (gp[i]<0 && x[i]>=xu[i]){
      gp[i] = 0;
    }
  }
  return (0);
}

/*
 * $Log: blmvm.cpp,v $
 * Revision 1.2  2008/05/16 11:37:50  matuzaki
 *
 * support for g++ v4.1 and v4.3
 *
 * Revision 1.1.1.1  2007/01/25 09:01:39  y-matsu
 *
 *
 * Revision 1.1.1.1  2006/09/14 10:33:25  y-matsu
 *
 *
 * Revision 1.4  2005/04/27 10:30:44  tsuruoka
 * add copyright
 *
 * Revision 1.3  2004/08/09 12:27:21  tsuruoka
 * change messages
 *
 * Revision 1.2  2004/07/27 07:43:42  tsuruoka
 * change stopping condition
 *
 * Revision 1.1  2004/07/26 13:10:55  tsuruoka
 * add files
 *
 * Revision 1.3  2004/07/10 05:59:35  tsuruoka
 * change stopping condition
 *
 * Revision 1.2  2004/07/08 11:43:12  tsuruoka
 * add early stopping
 *
 * Revision 1.1  2004/07/02 09:15:36  tsuruoka
 * add LMVM
 *
 */

