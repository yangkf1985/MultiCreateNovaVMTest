### 功能提示
异步并发创建或者删除虚拟机

### 使用方法
```
创建删除
python test_nova_case.py [test_type] [vm_num] [handle_operation]
test_type: 分为本地和ceph，本地存储分为SAS和SSD。这个参数和虚拟机的明明相关 
vm_num: 40, 60, 80, 100
handle_operation: 0-delete, 1-create

获取,获取当前创建的虚拟机的信息并生成csv文件
python get_test_result.py [test_type] [vm_num]
test_type: 分为本地和ceph，本地存储分为SAS和SSD。这个参数和虚拟机的明明相关 
vm_num: 40, 60, 80, 100
```
创建：
python test_nova_case.py local 1 1
删除：
python test_nova_case.py local 1 0
获取：
python get_test_result.py local 1

### 配置
```
sql_conn='mysql://autopool:autopoolpassword@192.168.111.2:3306/xipu_nova?charset=utf8' 
auth_url='http://192.168.10.10:35357/v2.0/tokens' 
tenant_name='admin' 
user_name='admin' 
user_password='admin_pass' 
region_name='RegionOne' 

default_network='de1fffda-85da-43d9-aa34-1435a59e76aa'
default_flavor='SAAS_50GB' 
default_image='SAAS_50G'

以上几个参数需要修改成测试环境的
修改options.py文件中：
{
        "name": 'config',
        "default": '/etc/TestNovaCase/test_nova_case.conf',
        "help": 'path of config file',
        "type": str,
        "callback": lambda path: parse_config_file(path, final=False)
}
config选项的default的值
```