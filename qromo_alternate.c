#include <math.h>
#include <stdio.h>
#define EPS 1.0e-9
// #define JMAX 14
#define JMAX 8
#define JMAXP (JMAX+1)
#define K 5

double qromo_alternate(double (*func)(double), double a, double b,
	double (*choose)(double(*)(double), double, double, int))
{
	void polint_alternate(double xa[], double ya[], int n, double x, double *y, double *dy);
	void nrerror(char error_text[]);
	int j;
	double ss,dss,h[JMAXP+1],s[JMAXP+1];

//	printf("Enter qromo_alternate....\n");

	h[1]=1.0;
	for (j=1;j<=JMAX;j++) {
		s[j]=(*choose)(func,a,b,j);
		if (j >= K) {
			polint_alternate(&h[j-K],&s[j-K],K,0.0,&ss,&dss);
//			if (fabs(dss) < EPS*fabs(ss)) {return ss;}
			if (j == JMAX) return ss;
		}
		s[j+1]=s[j];
		h[j+1]=h[j]/9.0;
	}
	nrerror("Too many steps in routing qromo_alternate");
	return 0.0;
}
#undef EPS
#undef JMAX
#undef JMAXP
#undef K
/* (C) Copr. 1986-92 Numerical Recipes Software #p21E6W)1.1&iE10(9p#. */
