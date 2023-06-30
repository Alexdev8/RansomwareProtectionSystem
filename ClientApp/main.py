import ClientApp.PopUp.popup as pop
import os
import tkinter as tk
from PIL import Image, ImageTk
from dotenv import load_dotenv
import ClientApp.load_vars as vars
import ClientApp.PCRéactivation.network_interfaces_to_up as reac
import psutil
import platform
from ClientApp.PCIsolation.test_loopback import is_loopback
from ClientApp.PCIsolation.test_loopback_mac import is_loopback_mac
from ClientApp.PCIsolation.test_loopback_linux import is_loopback_linux
from ClientApp.PCIsolation.interface_desactivation import disable_interfaces
from ClientApp.PCIsolation.interface_desactivation_linux import disable_interfaces_linux
from ClientApp.PCIsolation.interface_desactivation_mac import disable_interfaces_mac
import ClientApp.PCIsolation.network_interface_up_no_loopback
import ClientApp.PCRéactivation.network_interfaces_to_up
import ClientApp.PCRéactivation.reactivation_interface
import ClientApp.PCRéactivation.reactivation_interface_linux
import ClientApp.PCRéactivation.reactivation_interface_mac

a=pop.Message_Erreur(["Ethernet 2","Wi-Fi"])