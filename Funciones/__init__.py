# Funciones/__init__.py
from .inventario_manager import InventarioManager
from .crm import CRMManager
from .contabilidad import ContabilidadManager
from .dashboard import DashboardManager
from .ventas import VentasManager

__all__ = [
    'InventarioManager',
    'CRMManager',
    'ContabilidadManager',
    'DashboardManager',
    'VentasManager'
]
