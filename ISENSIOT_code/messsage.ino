void sendAndReceive(String message){
  String data = Serial.readStringUntil(" \n" );
  if(data == "aan"){
    on = 1;
  }
  if(data =="uit"){
    on = 0;
  }
  Serial.println(message);
}
