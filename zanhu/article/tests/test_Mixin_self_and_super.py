# 讨论django的Mixin类，self和super的用法

class B:  # === class B(object): # 这里B也可以表示为BMixin
    def log(self):
        print("B log")

    def display(self):
        print("B display")
        super(B, self).display2()
        self.log()
        # self.display2() # 这样也是可以实现的，因为这个是Mixin，当前类没有定义display2()，只要实例的MRO可以查找到即可，这里会输出实例test的定义A的"aa"


class C:
    def display2(self):
        print("C display")


class A(B, C):
    def log(self):
        print("A log")
        super(A, self).log()

    def display2(self):
        print("aa")


# test = A()
# test.display()

# 解析：这里实例test的MRO为A B C。
# 首先是查找display()，A类未定义方法，然后去B类查找到display()，输出“B display”。
# 然后在B类的display()下，还有super(B, self).display2()和self.log()。
# super(B, self).display2()表示在实例test的MRO上，对B类的super()父类查找display2()，这里可以在实例test的MRO查找顺序解析，得到C类定义的display2()，输出“C display”。
# 然后self.log()表示从实例test的MRO重新查找log()，得到A类实例的log()，输出“A log”
# 在A类定义的log()函数里还有super(A, self).log()，表示从A的super()父类里查找log()，即从A B C的A后继续查找log()，得到B类定义的log()函数，输出"B log"
# 函数解析完成

# 在django的类继承中，有很多Mixin后缀，就是可以表示BMixin
# 例如：
# b = B()
# b.display() # 这样则会出错，因为实例b没有super(B, self).display2()，super(B, self)等于object，而object没有定义display2函数，则这行代码会报错
# 所以Mixin的意思表示混入，无法单单声明实例B，但是可以借用BMixin来混入某些功能。
# 而super().function()则表示在当前类定义的“父类”去查找，则从当前类定义开始，从MRO向下查找。
