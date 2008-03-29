(*

category:      Test
synopsis:      Basic two reactions using functionDefinitions with three species 
               and parameters local to reactions.
componentTags: Compartment, Species, Reaction, FunctionDefinition 
testTags:      InitialAmount, LocalParameters
testType:      TimeCourse
levels:        2.1, 2.2, 2.3

The model contains one compartment named compartment.
  There are three species named S1, S2 and S3 and one parameter named k.
  The model contains two reactions defined as:

[{width:30em,left-margin:5em}| *Reaction* | *Rate* |
| S1 -> S2 | $k*S1*compartmen$  |
| S2 -> S3 | $multiply(S1,S2)*compartment,$  |]

Reaction S2 -> S3 defines one local parameter S1.  This parameter shadows the
species S1 and thus in reaction S2 -> S3 the value of the local parameter S1 should
be used.


The model contains one functionDefinition defined as:

[{width:30em,left-margin:5em}| *Id* | *Arguments* | *Formula* |
 | multiply | x, y | $x*y$ |]


The initial conditions are as follows:

[{width:30em,left-margin:5em}| | *Value* | *Units* |
|              Initial amount of S1:| $3.0 \x 10^-15$ | mole                      |
|              Initial amount of S2:| $            0$ | mole                      |
|              Initial amount of S3:| $            0$ | mole                      |
|              Value of parameter k:| $            2$ | second^-1^ |
|       Value of local parameter S1:| $            1$ | second^-1^ |
| Volume of compartment compartment:| $            1$ | litre                     |]

The species values are given as amounts of substance to make it easier to
use the model in a discrete stochastic simulator, but (as per usual SBML
principles) they must be treated as concentrations where they appear in
expressions.

*)

newcase[ "00134" ];

addFunction[ multiply, arguments -> {x, y}, math -> x*y];
addCompartment[ compartment, size -> 1 ];
addSpecies[ S1, initialAmount -> 3.0 10^-15];
addSpecies[ S2, initialAmount -> 0];
addSpecies[ S3, initialAmount -> 0];
addParameter[ k, value -> 2];
addReaction[ S1 -> S2, reversible -> False,
	     kineticLaw -> k*S1*compartment];
addReaction[ S2 -> S3, reversible -> False,
	     kineticLaw -> multiply[S1,S2]*compartment, parameters -> {S1 -> 1} ];

makemodel[]
