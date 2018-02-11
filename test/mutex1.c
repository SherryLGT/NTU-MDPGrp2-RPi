#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

int g_var1 = 0;	// global variable
pthread_mutex_t mutexA;

void *inc_gv()
{
	int i,j;

	//pthread_mutex_lock(&mutexA);
	for (i=0;i<10;i++)
	{
		g_var1++; // increment the global variable
		pthread_mutex_lock(&mutexA);
		for (j=0; j<5000000;j++); // delay loop
		printf(" %d",g_var1); // print the value
		fflush(stdout);
		pthread_mutex_unlock(&mutexA);
	}
	//pthread_mutex_unlock(&mutexA);
}

main()
{
	pthread_mutex_init(&mutexA, NULL);

	pthread_t TA, TB;
	int TAret, TBret;

	TAret = pthread_create(&TA, NULL, inc_gv, NULL);
	TBret = pthread_create(&TB, NULL, inc_gv, NULL);

	pthread_join(TAret, NULL);
	pthread_join(TBret, NULL);

	printf("\n mutex1 completed \n");
}
