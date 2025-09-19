import sys,os
x= [1,2,3,4,5]
def f( y ) :
 for i in range(0,len(y)):
     if i%2==0:print ( "even:",y[i] )
     else:
            print("odd:" ,y [ i ])
class person: 
 def __init__ (self,n,a):self.name=n;self.age=a
 def sayHi(self): print( "hi my name is",self.name,"and I am",self.age,"years old" )
def   main(  ):
    p=person( "Roma" ,20 )
    p.sayHi( )
    f( x )
    if True:print(   "done" );return
main( )