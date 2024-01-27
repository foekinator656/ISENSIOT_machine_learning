float runAvg_init (runAvg_t *runAvg, float initSample){
    for(int i = 0; i< RUNAVG_T_NSAMPLES; i++){
      runAvg->samples[i] = initSample;
    } 
    runAvg->iNewestSample = RUNAVG_T_NSAMPLES-1;  
    runAvg->runningSum = initSample*RUNAVG_T_NSAMPLES;
    
    return initSample;     
  }

float runAvg_update (runAvg_t *runAvg, float initSample){
  int iOldestSample = (runAvg->iNewestSample+1) % RUNAVG_T_NSAMPLES;

  runAvg->runningSum -= runAvg->samples[iOldestSample];
  runAvg->runningSum += initSample;
  runAvg->samples[iOldestSample] = initSample;
  runAvg->iNewestSample = iOldestSample;
  
  return runAvg->runningSum/RUNAVG_T_NSAMPLES;
}

int senseSpin(){
  int start = millis();
  if (leftOrRight == 0){
      myservo.write(90);
      leftOrRight =1;
  }
  else{
      myservo.write(0);
      leftOrRight =0 ;
  }

  runAvg_t runningAverage;
  runAvg_init (&runningAverage, 50);
  int spinTime = 0; 
  while (1) {
    if(spinTime>500){
      break;
    }
    sensorValue = analogRead(sensorPin);
    if(runAvg_update (&runningAverage, sensorValue)>30){
          spinTime+=1;
    }
    else if(spinTime>15){
      break;
    }

    delay(2);
  }
  return millis()-start;
}
