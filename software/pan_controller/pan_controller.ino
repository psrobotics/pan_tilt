#include <Wire.h>
#include "AS5600_mod.h"
#include "TCA9548A_mod.h"


TCA9548A device1;
AS5600 sensor;

float pitch_angle = 90;
float yaw_angle = 90;

class motor
{
  public:
    int pin1, pin2;
    int dir;

    motor(int p1, int p2, int ind);
    void pwm_run(int in);
    void keep_stop();
};
motor::motor(int p1, int p2, int ind)
{
  pin1 = p1;
  pin2 = p2;
  pinMode(pin1, OUTPUT);
  pinMode(pin2, OUTPUT);
  dir = ind;
}
void motor::pwm_run(int in)
{
  int absin = abs(in);
  if (in * dir > 0)
  {
    analogWrite(pin1, absin);
    analogWrite(pin2, 0);
  }
  else if (in * dir <= 0)
  {
    analogWrite(pin1, 0);
    analogWrite(pin2, absin);
  }
}
void motor::keep_stop()
{
  digitalWrite(pin1, 0);
  digitalWrite(pin2, 0);
}

class pid
{
  public:
    double target;
    double input;
    double kp, ki, kd;
    double esum, e0, e1;
    double pe, ie, de;
    double output;
    double output_range;

    pid(double p, double i, double d, double range);
    double cal(double in);
    void change_para(double np, double ni, double nd);
    void set_target(double tar);
    void set_range(double range);
};
pid::pid(double p, double i, double d, double range)
{
  kp = p; ki = i; kd = d;
  target = 0; input = 0;
  esum = 0; e0 = 0; e1 = 0;
  pe = 0; ie = 0; de = 0;
  output = 0;
  output_range = range;
}
double pid::cal(double in)
{
  input = in;
  e0 = target - input;//误差积分
  esum += e0;//误差微分
  de = e0 - e1;
  pe = e0;
  ie = esum;
  e1 = e0;
  output = pe * kp + ie * ki + de * kd; //二阶误差输入

  if (output > output_range)
    output = output_range;
  if (output < -1 * output_range)
    output = -1 * output_range;

  return output;
}
void pid::change_para(double np, double ni, double nd)
{
  kp = np; ki = ni; kd = nd;
}
void pid::set_target(double tar)
{
  target = tar;
}
void pid::set_range(double range)
{
  output_range = range;
}


class encoder
{
  public:
    int encoder_id;
    int read_raw;
    double angle_raw;
    double angle_pro;
    int dir;
    int offset;

    encoder(int id);
    int get_raw();
    double get_angleraw();
    double get_anglepro();
    void set_offset(double in);
    void set_dir(int in);
};

encoder::encoder(int id)
{
  encoder_id = id;
  dir = 1;
  offset = 0;
}
int encoder::get_raw()
{
  device1.set_port(encoder_id);
  read_raw = sensor.getAngle();
  return read_raw;
}
double encoder::get_angleraw()
{
  device1.set_port(encoder_id);
  read_raw = sensor.getAngle();
  angle_raw = (read_raw / 4096.0) * 360.0;


  if (dir == -1)
    angle_raw = 360 - angle_raw;

  return angle_raw;
}
double encoder::get_anglepro()
{
  device1.set_port(encoder_id);
  read_raw = sensor.getAngle();
  angle_raw = (read_raw / 4096.0) * 360.0;

  if (dir == -1)
    angle_raw = 360 - angle_raw;

  if (offset > 0)
  {
    if (angle_raw > 360 - offset && angle_raw <= 360)
      angle_pro = angle_raw - 360 + offset;
    else
      angle_pro = angle_raw + offset;
  }
  else
  {
    if (angle_raw >= 0 && angle_raw < abs(offset))
      angle_pro = angle_raw + 360 + offset;
    else
      angle_pro = angle_raw + offset;
  }

  return angle_pro;
}
void encoder::set_offset(double in)
{
  offset = in;
}
void encoder::set_dir(int in)
{
  dir = in;
}

encoder en_yaw(2), en_pitch(3);
pid pid_yaw(3.5, 0.001, 6, 255), pid_pitch(3.5, 0.001, 6, 255);
motor motor_yaw(9, 10, 1), motor_pitch(5, 6, 1);
double angle_test = 0;

union float2byte {
  float f; byte b[sizeof(float)];
};

void setup()
{
  Serial.begin(115200);
  device1.init();//init the unversial tca device

  en_yaw.set_offset(-353.58 + 90);
  en_pitch.set_offset(-278.53 + 90);
}

float clip(float in, float limit_up,float limit_down)
{
  if (in > limit_up)
    in = limit_up;
  if (in < limit_down)
    in = limit_down;
  return in;
}

void pos_update()
{
  en_yaw.get_anglepro();
  en_pitch.get_anglepro();

  pid_yaw.set_target(clip(pitch_angle,90+50,90-50));
  pid_pitch.set_target(clip(yaw_angle,90+50,90-50));

  motor_yaw.pwm_run(pid_yaw.cal(en_yaw.angle_pro));
  motor_pitch.pwm_run(pid_pitch.cal(en_pitch.angle_pro));
}

void loop()
{
  if (Serial.available() > 0)
  {
    if (Serial.read() == 'X')
    {
      pitch_angle = Serial.parseInt();
      if (Serial.read() == 'Y')
      {
        yaw_angle = Serial.parseInt();
        pos_update();
      }
    }
    while (Serial.available() > 0)
    {
      Serial.read();
      pos_update();
    }
  }

}
