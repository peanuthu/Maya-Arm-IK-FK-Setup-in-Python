'''
The following script will build up an IK/FK setup on an existing joint chain and match IK or FK position for future use. 
Last Edited on July 7, 2017

- Size of the FK controls is bigger
- After the FK/IK is created, nothing will be selected
- Search key word is 'palm' instead of 'hand'
-----------------
Edited on Jan. 9, 2018

- IK mode will turn on automatically if 'FK to IK' button's clicked;
- FK mode will turn on automatically if 'IK to FK' button's clicked;
-----------------
Edited on Oct. 11, 2017
- Arm IK pole vector axes are now following the 
- At line 64, it is still solved whether it should be - or +0.5. +/- determines whether the pole vector should be moved to the front or back
'''

import maya.cmds as cmds

#-------------------------------------------
#  Add IK Controls to the IK Joint Chain
#-------------------------------------------  
def ik_generator(ikShoulder):    
    # a. To generate an ikHandle for the shoulder - wrist joint 
    for child in cmds.listRelatives(ikShoulder[0],ad=True,type='joint'):        
        # a.2 Then to select the wrist joint
        if 'wrist' in child.lower():    
            cmds.select(child,add=True)
            wrist_joint=child
        elif 'elbow' in child.lower():
            elbow_joint=child
        # a.3 to check if there are still any extra joints not being deleted before    
        else:
            cmds.delete(child)    
            cmds.warning('Extra joints are deleted.')       
    # a.4 To generate an ikHandle based on selection    
    ik_handle=cmds.ikHandle(sol='ikRPsolver',n=wrist_joint+'_Handle')
	
    # b. To generate a control for the ikHandle  
    # b.1 To generate a nerb circle, and put it in a group.
    ik_control=cmds.circle(n=wrist_joint+'_Ctrl',nr=[1,0,0],degree=1,sections=4,ch=0)
    ik_group=cmds.group(ik_control[0],name=ik_control[0]+'Grp')
    # b.2 To match transform
    cmds.matchTransform(ik_group,wrist_joint)
    # b.3 To freeze the scale
    cmds.scale(4,4,4,ik_control)
    cmds.makeIdentity(ik_control,a=True,s=True,n=0,pn=True)
    # b.4 To orient constrain the wrist joint and the control
    cmds.orientConstraint(ik_control,wrist_joint,)
    # b.5 To parent the ik handle with the control
    cmds.parent(ik_handle[0],ik_control[0])
    # b.6 To hide the ik handle
    cmds.setAttr(ik_handle[0]+'.v',False)
    # b.7 To lock and hide scale attributes
    cmds.setAttr(ik_control[0]+'.sx',lock=True,keyable=False,channelBox=False)
    cmds.setAttr(ik_control[0]+'.sy',lock=True,keyable=False,channelBox=False)
    cmds.setAttr(ik_control[0]+'.sz',lock=True,keyable=False,channelBox=False)
    
    # c. To set up a pole vector    
    # c.1 To set up a locator with constraints
    pole_vec=cmds.spaceLocator(name=elbow_joint+'_PoleVec')
    cmds.matchTransform(pole_vec,elbow_joint,position=True)    
    cmds.aimConstraint(ikShoulder[0],wrist_joint,pole_vec,aim=[0.0,0.0,1.0],u=[0.0,1.0,0.0],wut='objectrotation',wu=[0.0,0.0,-1.0],wuo=elbow_joint)
    cmds.delete(pole_vec,constraints=True)    
    # c.2 To place the locator to the right position    
    # c.2.1 To determine the distance between the pole vector and the elbow joint
    wrist_pos=cmds.joint(wrist_joint,q=True,p=True)
    move_distance=abs(wrist_pos[0])*(-0.5)
    # c.2.2 To put the locator in a group
    pole_vecGrp=cmds.group(em=True,name=elbow_joint+'_PoleVectorGrp')
    # c.2.3 To place the locator at the right position
    cmds.move(0,0,move_distance,pole_vec,r=True,os=True)
    cmds.matchTransform(pole_vecGrp,pole_vec)
    # c.2.4 To make the locator a pole vector
    cmds.poleVectorConstraint(pole_vec,ik_handle[0])
    # c.3 To clear out the transform values of the pole vector
    cmds.parent(pole_vec,pole_vecGrp)
    # c.4 To hide the ik shoulder chain
    cmds.setAttr(ikShoulder[0]+'.v',False)
    # c.6 To hide rotation and scale attributes of the pole vector
    cmds.setAttr(pole_vec[0]+'.rx',lock=True,keyable=False,channelBox=False)
    cmds.setAttr(pole_vec[0]+'.ry',lock=True,keyable=False,channelBox=False)
    cmds.setAttr(pole_vec[0]+'.rz',lock=True,keyable=False,channelBox=False)
    cmds.setAttr(pole_vec[0]+'.sx',lock=True,keyable=False,channelBox=False)
    cmds.setAttr(pole_vec[0]+'.sy',lock=True,keyable=False,channelBox=False)
    cmds.setAttr(pole_vec[0]+'.sz',lock=True,keyable=False,channelBox=False)
    # c.7 To pass the variables to the main part
    return pole_vec,ik_control

    
#----------------------------------------
#  Add FK Controls to the FK Joint Chain
#----------------------------------------    
  
def fk_generator(fkShoulder,fk_locator):
    # a. To store the fk shoulder joint and all its descendents into an array
    cmds.select(fkShoulder[0],r=True)
    for child in cmds.listRelatives(fkShoulder[0],ad=True,type='joint'):
        cmds.select(child,add=True)    
    selection=cmds.ls(sl=True,type='joint')
    # b. To generate controls for each joint in the array
    # b.1 To set up an array to store all the controls
    fkGroups=[]
        
    for jnt in selection: 
        # b.2 To create a nerb circle with proper name
        fk_control=cmds.circle(name=jnt+'_Ctrl',nr=[1,0,0],ch=0)
        # b.2.1 To lock all the translate and scale values for the circle
        cmds.setAttr(fk_control[0]+'.tx',lock=True,keyable=False,channelBox=False)
        cmds.setAttr(fk_control[0]+'.ty',lock=True,keyable=False,channelBox=False)
        cmds.setAttr(fk_control[0]+'.tz',lock=True,keyable=False,channelBox=False)
        cmds.setAttr(fk_control[0]+'.sx',lock=True,keyable=False,channelBox=False)
        cmds.setAttr(fk_control[0]+'.sy',lock=True,keyable=False,channelBox=False)
        cmds.setAttr(fk_control[0]+'.sz',lock=True,keyable=False,channelBox=False)
        
        
        if 'shoulder' in jnt.lower():
            cmds.select(fk_control[0]+'.cv[0:7]',r=True)
            cmds.scale(10,10,10)
        elif 'elbow' in jnt.lower():
            cmds.select(fk_control[0]+'.cv[0:7]',r=True)
            cmds.scale(7,7,7)              
        else:
            cmds.select(fk_control[0]+'.cv[0:7]',r=True)
            cmds.scale(3.8,3.8,3.8)  
        # b.3 To generate a group for each circle with proper name
        grp=cmds.group(fk_control[0],name=fk_control[0]+'Grp')
        # b.3.1 To add the new group to the fkGroups so it can be returned later
        fkGroups.append(grp)
        cmds.matchTransform(grp,jnt)
        # b.4 To parent constrain the joint to the nerb
        cmds.parentConstraint(fk_control[0],jnt)
        # b.5 To parent the control group to its parent in the hierachy
        if cmds.listRelatives(jnt,p=True):
            parentJnt=cmds.listRelatives(jnt,p=True)
            if cmds.objExists((parentJnt[0]+'_Ctrl')):
                cmds.parent(grp,(parentJnt[0]+'_Ctrl'))
        if cmds.listRelatives(jnt,c=True,type='joint'):
            for child in cmds.listRelatives(jnt,c=True,type='joint'):
                if cmds.objExists(child+'_CtrlGrp'):
                    cmds.parent((child+'_CtrlGrp'),fk_control) 
    # c. To set up the fk locator pole vector for ik/fk match  
    for jnt in selection:
        # c.1 To store the fk elbow joint into a variable           
        if 'elbow' in jnt.lower():    
            fk_elbow=jnt
    # c.2 To set up a group at the fk shoulder joint      
    shoulderGrp=cmds.group(em=True,name=fkShoulder[0]+'PoleVecGroup')
    cmds.matchTransform(shoulderGrp,fkShoulder[0])
    # c.3 To set up a group at the fk elbow joint
    elbowGrp=cmds.group(em=True,name=fk_elbow+'PoleVecGroup')
    cmds.matchTransform(elbowGrp,fk_elbow)
    # c.4 To parent the groups 
    cmds.parent(elbowGrp,shoulderGrp)
    cmds.parent(fk_locator,elbowGrp)
    # c.5 To parent constraint the shoulder group to the shoulder. So the entire group moves when the shoulder rotates
    cmds.parentConstraint(fkShoulder[0],shoulderGrp)
    # c.6 To make it rotates when the elbow joint rotates
    rotMultiply=cmds.shadingNode('multiplyDivide',name=fk_elbow+'multiply',asUtility=True)    
    cmds.connectAttr(fk_elbow+'.rotateZ',rotMultiply+'.input1X',f=True)
    cmds.setAttr(rotMultiply+'.input2X',0.5)
    cmds.connectAttr(rotMultiply+'.outputX',elbowGrp+'.rotateZ')
    
    cmds.setAttr(fkShoulder[0]+'.v',False)
    
    return fkGroups    

#----------------------------------------
#         Generate IK&FK Switch
#----------------------------------------

def switch_generator(sel,fkShoulder,ikShoulder,fkGroups,pole_vecCtrl,ik_Ctrl):    
    # a. To create a nerb shape
    switch_control=cmds.circle(n='IK/FK_Switch_Ctrl',nr=[0,1,0],degree=1,sections=4,ch=0)
    # b. To place it near the original wrist joint    
    for child in cmds.listRelatives(sel[0],ad=True,type='joint'):
        if 'wrist' in child.lower():
            cmds.matchTransform(switch_control,child)
            wrist_joint=child
                
    cmds.move(0,2,0,switch_control,relative=True,os=True)  
    cmds.scale(1.5,1,0.5,switch_control,r=True) 
    cmds.scale(3,3,3,switch_control,r=True)      
    # c. To parent constrain the switch control with the original wrist joint
    cmds.parentConstraint(wrist_joint,switch_control,maintainOffset=True)    
    # d. To create a new attribute for the switch control
    cmds.select(switch_control,r=True)
    cmds.addAttr(ln='ikFkSwitch',at='float',min=0,max=1,dv=0.5)
    cmds.setAttr(switch_control[0]+'.ikFkSwitch',keyable=True)    
    # e. To lock and hide all other attributes
    cmds.setAttr(switch_control[0]+'.tx',lock=True,keyable=False,channelBox=False)
    cmds.setAttr(switch_control[0]+'.ty',lock=True,keyable=False,channelBox=False)
    cmds.setAttr(switch_control[0]+'.tz',lock=True,keyable=False,channelBox=False) 
    cmds.setAttr(switch_control[0]+'.rx',lock=True,keyable=False,channelBox=False)
    cmds.setAttr(switch_control[0]+'.ry',lock=True,keyable=False,channelBox=False) 
    cmds.setAttr(switch_control[0]+'.rz',lock=True,keyable=False,channelBox=False) 
    cmds.setAttr(switch_control[0]+'.sx',lock=True,keyable=False,channelBox=False) 
    cmds.setAttr(switch_control[0]+'.sy',lock=True,keyable=False,channelBox=False) 
    cmds.setAttr(switch_control[0]+'.sz',lock=True,keyable=False,channelBox=False) 
    cmds.setAttr(switch_control[0]+'.v',lock=True,keyable=False,channelBox=False)     
    # f. To build connections between IK and FK 
    # f.1 To store all joints into variables
    fk_shoulder_jnt=fkShoulder[0]
    for child in cmds.listRelatives(fkShoulder[0],ad=True,type='joint'):
        if 'elbow' in child.lower():
            fk_elbow_jnt=child
        elif 'wrist' in child.lower():
            fk_wrist_jnt=child
            
    ik_shoulder_jnt=ikShoulder[0]
    for child in cmds.listRelatives(ikShoulder[0],ad=True,type='joint'):
        if 'elbow' in child.lower():
            ik_elbow_jnt=child
        elif 'wrist' in child.lower():
            ik_wrist_jnt=child
    
    orig_shoulder_jnt=sel[0]       
    for child in cmds.listRelatives(sel[0],ad=True,type='joint'):
        if 'elbow' in child.lower():
            orig_elbow_jnt=child
        elif 'wrist' in child.lower():
            orig_wrist_jnt=child    

    # f.2 To create blendColors node
    shoulder_blend=cmds.shadingNode('blendColors',name=orig_shoulder_jnt+'Blend',asUtility=True)
    elbow_blend=cmds.shadingNode('blendColors',name=orig_elbow_jnt+'Blend',asUtility=True)    
    wrist_blend=cmds.shadingNode('blendColors',name=orig_wrist_jnt+'Blend',asUtility=True)
    # f.3 To connect IK/FK rotation attributes to the corresponding color blend attributes
    cmds.connectAttr(fk_shoulder_jnt+'.rotate',shoulder_blend+'.color1.')
    cmds.connectAttr(ik_shoulder_jnt+'.rotate',shoulder_blend+'.color2.')
    cmds.connectAttr(switch_control[0]+'.ikFkSwitch',shoulder_blend+'.blender.')
    cmds.connectAttr(shoulder_blend+'.output',orig_shoulder_jnt+'.rotate.')  
    
    cmds.connectAttr(fk_elbow_jnt+'.rotate',elbow_blend+'.color1.')
    cmds.connectAttr(ik_elbow_jnt+'.rotate',elbow_blend+'.color2.')
    cmds.connectAttr(switch_control[0]+'.ikFkSwitch',elbow_blend+'.blender.')
    cmds.connectAttr(elbow_blend+'.output',orig_elbow_jnt+'.rotate.')        
    
    cmds.connectAttr(fk_wrist_jnt+'.rotate',wrist_blend+'.color1.')
    cmds.connectAttr(ik_wrist_jnt+'.rotate',wrist_blend+'.color2.')
    cmds.connectAttr(switch_control[0]+'.ikFkSwitch',wrist_blend+'.blender.')
    cmds.connectAttr(wrist_blend+'.output',orig_wrist_jnt+'.rotate.')  
    
    # g. To let the IK/FK switch control the visibility of FK, Ik controls and joints
    vizFK_condition=cmds.shadingNode('condition',name='FK_Condition',asUtility=True)
    vizIK_condition=cmds.shadingNode('condition',name='IK_Condition',asUtility=True)    
    # g.1 To get all the control groups
    for fkgroup in fkGroups:               
        cmds.connectAttr(vizFK_condition+'.outColorR',fkgroup+'.v')
       
    cmds.connectAttr(switch_control[0]+'.ikFkSwitch',vizFK_condition+'.firstTerm')
    cmds.connectAttr(switch_control[0]+'.ikFkSwitch',vizIK_condition+'.firstTerm')
    cmds.setAttr(vizFK_condition+'.secondTerm',0)
    cmds.setAttr(vizIK_condition+'.secondTerm',1)
    # g.2 To let the condition control the visibility of the ik controls
    cmds.connectAttr(vizIK_condition+'.outColorR',pole_vecCtrl[0]+'.v')
    cmds.connectAttr(vizIK_condition+'.outColorR',ik_Ctrl[0]+'.v')


#----------------------------------------
#          Match Ik to FK
#----------------------------------------
def ikTofk(): 
    # a.1 To store a selection
    if cmds.ls(sl=True):
        selCtrl=cmds.ls(sl=True)
        # a.2 To prevent multiple items from being selected
        if len(selCtrl)==1:
            if selCtrl[0].endswith('_IK_Ctrl') or selCtrl[0].endswith('_IK_PoleVec'):
                # a.3 If the ik wrist control is selected
                if selCtrl[0].endswith('_IK_Ctrl'): 
                    # a.3.1 To match the wrist control to the fk wrist joint
                    fkWrist=selCtrl[0].replace('_IK_Ctrl','_FK')
                    cmds.matchTransform(selCtrl,fkWrist)
                    # a.3.2 Then to match the ik pole vector to the fk pole vector
                    fkElbow=cmds.listRelatives(fkWrist,p=True)
                    ikElbowPoleVec=fkElbow[0].replace('_FK','_IK_PoleVec')
                    fkElbowPoleVec=fkElbow[0]+'_PoleVec'
                    cmds.matchTransform(ikElbowPoleVec,fkElbowPoleVec)
                                        
                # a.4 If the ik pole vector is selected
                else: 
                    # a.4.1 To match the pole vectors 
                    fkElbowPoleVec=selCtrl[0].replace('_IK_PoleVec','_FK_PoleVec')
                    cmds.matchTransform(selCtrl,fkElbowPoleVec)
                    # a.4.2 To match the wrist control to the fk wrist joint
                    ikElbow=selCtrl[0].replace('_PoleVec','')
                    fkElbow=selCtrl[0].replace('_IK_PoleVec','_FK')
                    fkWrist=cmds.listRelatives(fkElbow,c=True)
                    ikWrist=cmds.listRelatives(ikElbow,c=True)
                    ikWristCtrl=ikWrist[0]+'_Ctrl'
                    cmds.matchTransform(ikWristCtrl,fkWrist[0])
                
                # turn on FK, turn off IK
                switchCtrl='IK_FK_Switch_Ctrl'
                cmds.setAttr(switchCtrl+'.ikFkSwitch',1)
                cmds.select(cl=True)  
                
                
            else:
                cmds.warning('Please select an IK control.')
        else: 
            cmds.warning('Please select only one control.')           
    else:
        cmds.warning('Please select a control')

#----------------------------------------
#          Match FK to IK
#----------------------------------------        

def fkToik():
    # a.1 To store a selection
    if cmds.ls(sl=True):
        selCtrl=cmds.ls(sl=True)
        # a.2 To prevent multiple items from being selected
        if len(selCtrl)==1:
            if selCtrl[0].endswith('_FK_Ctrl'):                
                # a.3 To match the fk joints to the corresponding ik joints
                # a.3.1 To find the root of the control hierarechy              
                root = cmds.ls(selCtrl,l=True)[0].split("|")[1]
                # a.3.2 To match the shoulder joints position
                for ctrl in cmds.listRelatives(root,ad=True):
                    if 'shoulder' in ctrl.lower():
                        fkShoulderCtrl=ctrl
                        ikShoulder=fkShoulderCtrl.replace('_FK_CtrlShape','_IK')
                        cmds.matchTransform(fkShoulderCtrl,ikShoulder)
                    # a.3.3 To match the elbow joints position
                    elif 'elbow' in ctrl.lower():
                        print ctrl
                        fkElbowCtrl=ctrl
                        ikElbow=fkElbowCtrl.replace('_FK_CtrlShape','_IK')
                        cmds.matchTransform(fkElbowCtrl,ikElbow)
                    # a.3.4 To match the wrist joints position
                    elif 'wrist' in ctrl.lower():
                        fkWristCtrl=ctrl
                        ikWrist=fkWristCtrl.replace('_FK_CtrlShape','_IK')
                        cmds.matchTransform(fkWristCtrl,ikWrist)
                    else:
                        return
                        
                # turn on IK, turn off FK        
                switchCtrl='IK_FK_Switch_Ctrl'
                cmds.setAttr(switchCtrl+'.ikFkSwitch',0) 
                cmds.select(cl=True)            
                        
            else:
                cmds.warning('Please select a FK control.')               
        else:            
            cmds.warning('Please select only one control.')
    else: 
        cmds.warning('Please select a control.')    

#----------------------------------------
#       Create IK & FK Joint Chain
#----------------------------------------
    
def create_joints():
    # a. To make sure a joint is selected
    if cmds.ls(sl=True,type='joint'):
        sel=cmds.ls(sl=True)   
        # a.1 To check if multiple joints are selected
        if len(sel)!=1:
            cmds.warning('Please select only one joint.')        
        # a.2 To check whether the selected joint has any child joint
        elif not cmds.listRelatives(sel[0],c=True,type='joint'):
            cmds.warning('The joint has no child.')       
        # b. To duplicate the selected shoulder joint, to remove extra joints, and to give proper names;
        elif 'shoulder' in sel[0].lower():         
            # b.1 To duplicate the selected shoulder joint as IK
            ikShoulder=cmds.duplicate(sel[0],rc=True,name=sel[0]+'_IK')       
            for child in cmds.listRelatives(ikShoulder[0],ad=True,type='joint'):                
                #b.2 To delete forearm and hand joints
                if 'forearm' in child.lower():
                    cmds.delete(child)
                elif 'palm' in child.lower():
                    cmds.delete(child) 
                elif 'thum' in child.lower():
                    cmds.delete(child)                   
                #b.3 To properly rename the rest joints
                else:
                    # To remove the last digit added by maya
                    newName=child[:-1]
                    # To add IK to the names
                    cmds.joint(child,e=True,name=newName+'_IK')
                                       
            #c.1 To duplicate the selected shoulder joint as FK       
            fkShoulder=cmds.duplicate(sel[0],rc=True,name=sel[0]+'_FK')            
            for child in cmds.listRelatives(fkShoulder[0],ad=True,type='joint'):                
                #c.2 To delete forearm and hand joints
                if 'forearm' in child.lower():
                    cmds.delete(child)
                elif 'palm' in child.lower():
                    cmds.delete(child)
                elif 'thum' in child.lower():
                    cmds.delete(child)                       
                #c.3 To properly rename the rest joints properly
                else:
                    newName=child[:-1]
                    cmds.joint(child,e=True,name=newName+'_FK')
        		
    		   # d. To call the ik generator function and store the returned controls into variables
            control_shapes=ik_generator(ikShoulder)   
            pole_vecCtrl=control_shapes[0]
            ik_Ctrl=control_shapes[1]
            
            # e. To set up a locator for IK/FK match, it will be further modified in the fk_generator[] function
            fk_locator=cmds.spaceLocator(name=pole_vecCtrl[0].replace('_IK_PoleVec','')+'_FK_PoleVec')
            cmds.matchTransform(fk_locator,pole_vecCtrl)
            cmds.setAttr(fk_locator[0]+'.v',False)
            # f. To call the fk generator function and store the returned controls into variables
            fkGroups=fk_generator(fkShoulder,fk_locator)
           
            # g. To generate an IK/FK switch and pass variables returned from other functions
            switch_generator(sel,fkShoulder,ikShoulder,fkGroups,pole_vecCtrl,ik_Ctrl)
            
            cmds.select(cl=True)                 
    
        else:
            cmds.warning('Please select a shoulder joint.')
    else:
        cmds.warning('Please select a joint.')    

#----------------------------------------
#           Create Window
#----------------------------------------

if cmds.window('IKFKBuilder',exists=True):
    cmds.deleteUI('IKFKBuilder')
    
ui_window=cmds.window('IKFKBuilder',title = "IK & FK BUILDER", w=400,h=150)
cmds.rowColumnLayout(nc=1,cw=[1,400])
cmds.showWindow(ui_window)
cmds.text(l='',h=10)
cmds.text(l='STEP 1: Please select a shoulder joint then hit Create',h=15)
cmds.text(l='',h=5)
cmds.button(l='Create',command='create_joints()')
cmds.text(l='',h=10)
cmds.text(l='STEP 2: Please select any one of the IK or FK controls',h=15)
cmds.text(l='',h=5)
cmds.rowLayout(nc=2,cw=[2,400],w=400) 

cmds.button(l='IK to FK',w=200,command='ikTofk()')
cmds.button(l='FK to IK',w=200,command='fkToik()')
    
    
