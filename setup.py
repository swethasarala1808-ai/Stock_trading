from setuptools import setup, find_packages

<<<<<<< HEAD
setup(
    name="stock_app",
    version="1.0.0",
    description="Stock Trading and Brokerage Management Platform",
    author="Swetha Sarala",
    author_email="swethasarala1808@gmail.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[],
=======
with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="stock_app",
    version="1.0.0",
    description="Stock Trading App for Frappe/ERPNext",
    author="Stock App",
    author_email="admin@example.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
>>>>>>> 1d8b324a77ed9333e48a012b11446f488c4a4b47
)
