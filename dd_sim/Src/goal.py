#!/usr/bin/env python

import rospy
import pyaudio
import time
import speech_recognition as sr

import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal

r = sr.Recognizer()
bot_state = 0


KeyWord = {"ไปที่":"go to",
	    "ไปที่อาหาร":"food",
            "ไปที่ของเล่น":"toy",
            "ไปที่เครื่องมือ":"electronic",
            "ไปที่กีฬา":"sport",
            "ไปที่เครื่องสำอาง":"cosmetics",
            "กลับไปจุดเริ่มต้น":"Standby_Station"         
            }



Goal = {"food":[-5.05,0,0,-1.5707],
        "toy":[-1.100765,1.5,0,-1.5707],
        "electronic":[1.822876,2,0,-1.5707],
        "sport":[3.804829,0,0,-1.5707],
        "cosmetic":[5.900340,-2.370142,0,0],
        
        "Standby_Station":[5,4,0,0]}




def movebase_client(map_odom_desire):

    client = actionlib.SimpleActionClient('move_base',MoveBaseAction)
 
    client.wait_for_server()

    goal = MoveBaseGoal()
    goal.target_pose.header.frame_id = "map"
    goal.target_pose.header.stamp = rospy.Time.now()

    goal.target_pose.pose.position.x = map_odom_desire[0]
    goal.target_pose.pose.position.y = map_odom_desire[1]

    goal.target_pose.pose.orientation.z = map_odom_desire[3]
    goal.target_pose.pose.orientation.w = map_odom_desire[2]

    client.send_goal(goal)
    wait = client.wait_for_result()
    if not wait:
        rospy.logerr("Action server not available!")
        rospy.signal_shutdown("Action server not available!")
    else:
        return client.get_result()   

if __name__ == '__main__':
    try:
        rospy.init_node('movebase_client_py')
        
        while 1:
            try:
                rospy.loginfo("Setting MIC: Say Something . . .")
                with sr.Microphone() as source:
                    audio = r.listen(source)
                    word = r.recognize_google(audio,language='th')
                    rospy.loginfo("Mic testing . . . STATUS: OK")
                    break

            except:
                rospy.loginfo("Setting MIC: Say Something . . .")



        while 1:
            if (bot_state == 0): #go to station
               rospy.loginfo("Going to . . . Standby_Station")
               result = movebase_client(Goal["Standby_Station"])
               if result:
               	rospy.loginfo("Arrive at the Standby-Station")
               	bot_state = 1
        
            elif (bot_state == 1): #ready to go
               rospy.loginfo("ready to get command")
               bot_state = 2

            elif (bot_state == 2):  #waiting for command
                try:
                    with sr.Microphone() as source:                
                        audio = r.listen(source)
                        word = r.recognize_google(audio,language='th')
                        try:
                            rospy.loginfo("Going to . . . " + KeyWord[word])
                            result = movebase_client(Goal[KeyWord[word]])
                            if result:
                                rospy.loginfo("Arrive at desired room")
                                bot_state = 3
                        except:
                            rospy.loginfo("Can't decode your voice, pls say again")
                            rospy.loginfo("Command Example : ไปที่")
                            pass

                except:
                    pass

            elif (bot_state == 3):  
                rospy.loginfo("Wait for interaction . . .")
                time.sleep(10)
                rospy.loginfo("interaction complete!")
                bot_state = 1


    except rospy.ROSInterruptException:
        rospy.loginfo("Navigation test finished.")
