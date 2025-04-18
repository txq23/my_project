from setuptools import find_packages, setup
import os
from glob import glob  # 添加 glob 导入
package_name = 'ackermann_car'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
            ('share/ament_index/resource_index/packages',
                ['resource/' + package_name]),
            ('share/' + package_name, ['package.xml']),
            
            # 安装 launch 文件
            (os.path.join('share', package_name, 'launch'), 
            glob('launch/*.launch.py')),
            
            # 安装 worlds 文件
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
             'motion_controller = ackermann_car.nodes.motion_controller:main',
        ],
    },
)
