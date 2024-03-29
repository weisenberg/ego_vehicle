import glob
import os
import sys

try:
    sys.path.append(glob.glob('/opt/carla-simulator/PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

import random
import time
import numpy as np
import cv2

# lidar attribute values
lidar_upper_fov = 15.0
lidar_lower_fov = -15.0
lidar_range = 100
lidar_rotation_frequency = 10
lidar_channels = 64
lidar_pointsPerSecond = 512000
lidar_dropoff_general_rate = 0
lidar_dropoff_intensity_limit = 0
    
actor_list = []
try:
    client = carla.Client('localhost', 2000)
    client.set_timeout(2.0)

    world = client.get_world()

    blueprint_library = world.get_blueprint_library()
    bp = blueprint_library.filter('model3')[0]
    spawn_point = random.choice(world.get_map().get_spawn_points())
    ego_vehicle = world.spawn_actor(bp, spawn_point)
    ego_vehicle.set_autopilot(True)
    
    actor_list.append(ego_vehicle)
    
    
    # --------------
    # add LIDAR sensor
    # --------------
    lidar_bp = world.get_blueprint_library().find('sensor.lidar.ray_cast')
    lidar_bp.set_attribute('channels', f'{lidar_channels}')
    lidar_bp.set_attribute('upper_fov', f'{lidar_upper_fov}')
    lidar_bp.set_attribute('lower_fov', f'{lidar_lower_fov}')
    lidar_bp.set_attribute('range', f'{lidar_range}')
    lidar_bp.set_attribute('points_per_second', f'{lidar_pointsPerSecond}')
    lidar_bp.set_attribute('rotation_frequency', f'{lidar_rotation_frequency}')
    lidar_bp.set_attribute('dropoff_general_rate', f'{lidar_dropoff_general_rate}')
    lidar_bp.set_attribute('dropoff_intensity_limit', f'{lidar_dropoff_intensity_limit}')

    lidar_location = carla.Location(x=0.0, y=0.0, z=2.4)
    lidar_rotation = carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0)
    lidar_spawn_point = carla.Transform(lidar_location, lidar_rotation)

    lidar_sensor = world.spawn_actor(lidar_bp, lidar_spawn_point, attach_to=ego_vehicle, attachment_type=carla.AttachmentType.Rigid)
    actor_list.append(lidar_sensor)

    

    # --------------
    # add IMU sensor
    # --------------

    imu_bp = world.get_blueprint_library().find('sensor.other.imu')

    imu_bp.set_attribute('sensor_tick', '0.02') #50Hz update rate
    imu_bp.set_attribute('noise_accel_stddev_x', '0.0') #noise-free IMU sensor
    imu_bp.set_attribute('noise_accel_stddev_y', '0.0')
    imu_bp.set_attribute('noise_accel_stddev_z', '0.0')
    imu_bp.set_attribute('noise_gyro_stddev_x', '0.0')
    imu_bp.set_attribute('noise_gyro_stddev_y', '0.0')
    imu_bp.set_attribute('noise_gyro_stddev_z', '0.0')

    imu_spawn_point = carla.Transform(carla.Location(x=0.0, y=0.0, z=0.7))
    ego_imu = world.spawn_actor(imu_bp, imu_spawn_point, attach_to=ego_vehicle, attachment_type=carla.AttachmentType.Rigid)
    actor_list.append(ego_imu)
    
    
    # --------------
    # place spectator on ego spawning
    # --------------
    while True:
        #channels = lidar_sensor.attributes.get('channels')
        #print(channels)
        spectator = world.get_spectator()
        
        # ---------------
        # to locate the spectator above the earth.
        # ---------------
#        spectator_location = carla.Location(ego_vehicle.get_transform().location + carla.Location(x=-4,z=4))
        # this part doesnt work:
#        spectator_rotation = carla.Rotation(ego_vehicle.get_transform().Rotation + carla.Rotation(pitch=-30))
#        spectator.set_transform(carla.Transform(spectator_location, spectator_rotation))

        spectator_transform =  ego_vehicle.get_transform()
        spectator_transform.location += carla.Location(x = 0, y=0, z = 3.0)
        spectator.set_transform(spectator_transform)

    time.sleep(5)

finally:

    print('destroying actors')
    for actor in actor_list:
        actor.destroy()
    print('done.')
