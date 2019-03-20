#include <Servo.h>
Servo servoX;
Servo servoY;
int middle = 83;
int iterations = 0;

int pixelsToDegree(String axis){
  int side = (Serial.read() - '0');
  int incomingLenght = (Serial.read() - '0');
  String pixels;
  for(int x=incomingLenght; x>0; x--){
    pixels.concat(Serial.read() - '0');
  }
  int pixels_int = pixels.toInt();
  int degree;
  if(side == -3){pixels_int *= -1;}
  if(axis == "x"){
    degree = round(pixels_int/11)+servoX.read();
    if(degree > 143 || degree < 23){degree=0;}
  }
  if(axis == "y"){
    degree = round(pixels_int/10)+servoY.read();
    if(degree > 103 || degree < 63){degree=0;}
  }
  return degree;
}

void directionAndWriteX(int side){
  int currentToDegree = servoX.read()+side;
  servoX.write(currentToDegree);
  delay(30);  
}
void directionAndWriteY(int side){
  int currentToDegree = servoY.read()+side;
  servoY.write(currentToDegree);
  delay(50);  
}
void rotate(int toDegreeX, int toDegreeY){
  int servoXat = servoX.read();
  int servoYat = servoY.read();
  if(servoXat > toDegreeX || servoYat > toDegreeY || servoXat < toDegreeX || servoYat < toDegreeY){
    while(servoX.read() > toDegreeX || servoX.read() < toDegreeX || servoY.read() > toDegreeY || servoY.read() < toDegreeY){
      servoXat = servoX.read();
      servoYat = servoY.read();
      if(servoXat > toDegreeX){directionAndWriteX(-1);}
        else if(servoXat < toDegreeX){directionAndWriteX(+1);}
      if(servoYat > toDegreeY){directionAndWriteY(-1);} 
        else if(servoYat < toDegreeY){directionAndWriteY(+1);}
    }
  }
}
void fire(int rounds){
  digitalWrite(2, HIGH);
  for(rounds; rounds>0; rounds--){
    delay(500);
  }
  digitalWrite(2, LOW); 
}

void setup() {
  pinMode(2, OUTPUT);
  servoX.attach(8);
  servoY.attach(9);
  Serial.begin(9600);
  rotate(middle+30, middle);
}
 
void loop() {
  digitalWrite(2, LOW);
  int xDegree = 0;
  int yDegree = 0;
  for(int i=0; i<50; i++){
     if((Serial.read() - '0') == -1){
      delay(100);
      xDegree = pixelsToDegree("x"); 
      if((Serial.read() - '0') == -1){
        yDegree = pixelsToDegree("y");
        rotate(xDegree, yDegree);
        fire(3);
        delay(200);
        break;
      }
    }
    delay(100);
  }
  iterations +=1;
  if (iterations % 2) {
    rotate(middle-30, middle);
    Serial.print(F("left"));
    Serial.flush();
    }
    else{
      rotate(middle+30, middle);
      Serial.print(F("right"));
      Serial.flush();
    }
}
