from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'ackermann_car'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),  # 自动发现包
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), 
         glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'worlds'),
         glob('worlds/*.sdf')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='wcy',
    maintainer_email='wcy@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'world_controller = ackermann_car.controller.world_ctrl:main',
        ],
    },
)
