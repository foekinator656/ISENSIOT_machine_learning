void regulate(float temp){
  if(on == 0){
    digitalWrite(heatPin, LOW);
    return;
  }
  if(temp+0.5<targettemp){
      digitalWrite(heatPin, HIGH);
    } else if (temp-0.5>targettemp){
      digitalWrite(heatPin, LOW);
    }
}
