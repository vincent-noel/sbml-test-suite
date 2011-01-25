(* 

category:      Test
synopsis:      Competing events with the same priority, jointly causing a parameter to monotonically increase, checking to make sure one event doesn't severly out-compete the other.  NOTE:  STOCHASTIC TEST. Your software may fail periodically; it is only supposed to succeed in the majority of cases.
componentTags: Parameter, EventNoDelay, EventPriority, AssignmentRule
testTags:      InitialValue, CSymbolTime, RandomEventExecution
testType:      TimeCourse
levels:        3.1
generatedBy:   Analytic

This model contains two events with the same trigger, the same priority, both set 'persistent=true', and both of which disable the trigger of the other.  This means that every .01 seconds, one fires and the other does not, at random, and increases the parameters Q or R, respectively.  A third parameter, S, is assigned the value of Q+R, meaning that it doesn't matter which one fires; S will increase monotonically.  A final parameter, 'error' checks to make sure neither Q nor R are chosen more frequently than the other--if the difference gets higher than 0.05, it triggers. 
 
The events are:

[{width:30em,margin-left:5em}| | *Trigger*   | *Delay* | *Assignments* |
 | Qinc | $time - reset >= 0.01$ | $-$   | $Q = Q + 0.01, reset = time$      |
 | Rinc | $time - reset >= 0.01$ | $-$   | $R = R + 0.01, reset = time$      |
 | error_check       | abs(Q-R) >= 15$ | $-$     | $error = 1$      |]


 The initial conditions are as follows:

[{width:30em,margin-left:5em}| |*Value*|
|Value of parameter Q          |$0$  |
|Value of parameter R          |$0$  |
|Value of parameter S          |$0$  |
|Value of parameter reset      |$0$  |
|Value of parameter error      |$0$  |]

 Note:  The 'error' parameter is a stochastic test, and may not always remain at '0' for all runs.  If your software fails, try running it again with a new random number seed, and it may succeed.  The value of '15' was chosen to be reasonable in the wide majority of cases, but still low enough to reveal problems in software that tends to pick one event over the other in a non-50/50 ratio.
 
Note 2: The test data for this model was generated from an analytical
solution of the system of equations.
*)

(*
//Antimony version of the file (without 'persistence' flagged)
model case00952()

  // Assignment Rules:
  S := Q + R;

  // Events:
  Qinc: at geq(time - reset, 0.01): Q = Q + 0.01, reset = time;
  Rinc: at geq(time - reset, 0.01): R = R + 0.01, reset = time;
  error_check: at geq(abs(Q - R), 15): error = 1;

  // Variable initializations:
  reset = 0;
  Q = 0;
  R = 0;
  error = 0;

  //Other declarations:
  var reset, Q, R, error, S;
end
*)
