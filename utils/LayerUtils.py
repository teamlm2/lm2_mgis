#!/usr/bin/python
# -*- coding: utf-8
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import QSqlDatabase
from qgis.core import *

from SessionHandler import SessionHandler
from ..model.ClPlanType import *
from ..model import SettingsConstants
from ..model import Constants
from ..model.LM2Exception import LM2Exception
import os

class LayerUtils(object):

    @staticmethod
    def layer_by_name(layer_name):
        layers = QgsMapLayerRegistry.instance().mapLayers()

        for id, layer in layers.iteritems():
            if layer.name() == layer_name:
                return layer

        return None

    @staticmethod
    def layer_by_data_source(schema_name, table_name):

        layers = QgsMapLayerRegistry.instance().mapLayers()

        for id, layer in layers.iteritems():
            if layer.type() == QgsMapLayer.VectorLayer:
                uri_string = layer.dataProvider().dataSourceUri()
                uri = QgsDataSourceURI(uri_string)
                if uri.table() == table_name:
                    if uri.schema() == schema_name:
                        return layer

    @staticmethod
    def load_layer_by_name(layer_name, id, restrictions=[]):

        restrictions = restrictions.split(",")

        if len(restrictions) > 0:
            for restriction in restrictions:
                restriction = restriction.strip()
                uri = QgsDataSourceURI()
                user = QSettings().value(SettingsConstants.USER)
                db = QSettings().value(SettingsConstants.DATABASE_NAME)
                host = QSettings().value(SettingsConstants.HOST)
                port = QSettings().value(SettingsConstants.PORT, "5432")
                pwd = SessionHandler().current_password()

                uri.setConnection(host, port, db, user, pwd)
                uri.setDataSource("s" + restriction, layer_name, "geometry", "", id)

                vlayer = QgsVectorLayer(uri.uri(), "s" + restriction + "_" + layer_name, "postgres")
                QgsMapLayerRegistry.instance().addMapLayer(vlayer)
                return vlayer

    @staticmethod
    def load_union_layer_by_name(layer_name, id):

        uri = QgsDataSourceURI()
        user = QSettings().value(SettingsConstants.USER)
        db = QSettings().value(SettingsConstants.DATABASE_NAME)
        host = QSettings().value(SettingsConstants.HOST)
        port = QSettings().value(SettingsConstants.PORT, "5432")
        pwd = SessionHandler().current_password()

        uri.setConnection(host, port, db, user, pwd)
        uri.setDataSource("data_soums_union", layer_name, "geometry", "", id)

        vlayer = QgsVectorLayer(uri.uri(), "data_soums_union" + "_" + layer_name, "postgres")
        QgsMapLayerRegistry.instance().addMapLayer(vlayer, False)
        return vlayer

    @staticmethod
    def load_ub_data_layer_by_name(layer_name, id):

        uri = QgsDataSourceURI()
        user = QSettings().value(SettingsConstants.USER)
        db = QSettings().value(SettingsConstants.DATABASE_NAME)
        host = QSettings().value(SettingsConstants.HOST)
        port = QSettings().value(SettingsConstants.PORT, "5432")
        pwd = SessionHandler().current_password()

        uri.setConnection(host, port, db, user, pwd)
        uri.setDataSource("data_ub", layer_name, "geometry", "", id)

        vlayer = QgsVectorLayer(uri.uri(), layer_name, "postgres")
        QgsMapLayerRegistry.instance().addMapLayer(vlayer, False)
        return vlayer

    @staticmethod
    def load_layer_by_name_report(layer_name, id, restrictions=[]):

        restrictions = restrictions.split(",")

        if len(restrictions) > 0:
            for restriction in restrictions:
                restriction = restriction.strip()
                uri = QgsDataSourceURI()
                user = QSettings().value(SettingsConstants.USER)
                db = QSettings().value(SettingsConstants.DATABASE_NAME)
                host = QSettings().value(SettingsConstants.HOST)
                port = QSettings().value(SettingsConstants.PORT, "5432")
                pwd = SessionHandler().current_password()

                uri.setConnection(host, port, db, user, pwd)
                uri.setDataSource("s" + restriction, layer_name, "geometry", "", id)

                vlayer = QgsVectorLayer(uri.uri(), layer_name, "postgres")
                QgsMapLayerRegistry.instance().addMapLayer(vlayer,False)
                return vlayer

    @staticmethod
    def load_tmp_layer_by_name(layer_name, id, shema):

        uri = QgsDataSourceURI()
        user = QSettings().value(SettingsConstants.USER)
        db = QSettings().value(SettingsConstants.DATABASE_NAME)
        host = QSettings().value(SettingsConstants.HOST)
        port = QSettings().value(SettingsConstants.PORT, "5432")
        pwd = SessionHandler().current_password()

        uri.setConnection(host, port, db, user, pwd)
        uri.setDataSource(shema, layer_name, "geometry", "", id)

        vlayer = QgsVectorLayer(uri.uri(), layer_name, "postgres")
        QgsMapLayerRegistry.instance().addMapLayer(vlayer, False)
        return vlayer

    @staticmethod
    def load_layer_by_name_equipment(layer_name, id):

        uri = QgsDataSourceURI()
        user = QSettings().value(SettingsConstants.USER)
        db = QSettings().value(SettingsConstants.DATABASE_NAME)
        host = QSettings().value(SettingsConstants.HOST)
        port = QSettings().value(SettingsConstants.PORT, "5432")
        pwd = SessionHandler().current_password()

        uri.setConnection(host, port, db, user, pwd)
        uri.setDataSource("settings", layer_name, "geometry", "", id)

        vlayer = QgsVectorLayer(uri.uri(), layer_name, "postgres")
        QgsMapLayerRegistry.instance().addMapLayer(vlayer, False)
        return vlayer

    @staticmethod
    def load_layer_base_layer(layer_name, id, schema_name):

        uri = QgsDataSourceURI()
        user = QSettings().value(SettingsConstants.USER)
        db = QSettings().value(SettingsConstants.DATABASE_NAME)
        host = QSettings().value(SettingsConstants.HOST)
        port = QSettings().value(SettingsConstants.PORT, "5432")
        pwd = SessionHandler().current_password()

        uri.setConnection(host, port, db, user, pwd)
        uri.setDataSource(schema_name, layer_name, "geometry", "", id)

        vlayer = QgsVectorLayer(uri.uri(), layer_name, "postgres")
        QgsMapLayerRegistry.instance().addMapLayer(vlayer, False)
        return vlayer

    @staticmethod
    def load_polygon_layer_base_layer(layer_name, id, schema_name):

        uri = QgsDataSourceURI()
        user = QSettings().value(SettingsConstants.USER)
        db = QSettings().value(SettingsConstants.DATABASE_NAME)
        host = QSettings().value(SettingsConstants.HOST)
        port = QSettings().value(SettingsConstants.PORT, "5432")
        pwd = SessionHandler().current_password()

        uri.setConnection(host, port, db, user, pwd)
        uri.setDataSource(schema_name, layer_name, "polygon_geom", "", id)

        vlayer = QgsVectorLayer(uri.uri(), layer_name, "postgres")
        QgsMapLayerRegistry.instance().addMapLayer(vlayer, False)
        return vlayer

    @staticmethod
    def load_point_layer_base_layer(layer_name, id, schema_name):

        uri = QgsDataSourceURI()
        user = QSettings().value(SettingsConstants.USER)
        db = QSettings().value(SettingsConstants.DATABASE_NAME)
        host = QSettings().value(SettingsConstants.HOST)
        port = QSettings().value(SettingsConstants.PORT, "5432")
        pwd = SessionHandler().current_password()

        uri.setConnection(host, port, db, user, pwd)
        uri.setDataSource(schema_name, layer_name, "point_geom", "", id)

        vlayer = QgsVectorLayer(uri.uri(), layer_name, "postgres")
        QgsMapLayerRegistry.instance().addMapLayer(vlayer, False)
        return vlayer

    @staticmethod
    def load_line_layer_base_layer(layer_name, id, schema_name):

        uri = QgsDataSourceURI()
        user = QSettings().value(SettingsConstants.USER)
        db = QSettings().value(SettingsConstants.DATABASE_NAME)
        host = QSettings().value(SettingsConstants.HOST)
        port = QSettings().value(SettingsConstants.PORT, "5432")
        pwd = SessionHandler().current_password()

        uri.setConnection(host, port, db, user, pwd)
        uri.setDataSource(schema_name, layer_name, "line_geom", "", id)

        vlayer = QgsVectorLayer(uri.uri(), layer_name, "postgres")
        QgsMapLayerRegistry.instance().addMapLayer(vlayer, False)
        return vlayer

    @staticmethod
    def load_layer_by_name_admin_units(layer_name, id, restrictions=[]):

        restrictions = restrictions.split(",")

        if len(restrictions) > 0:
            for restriction in restrictions:
                restriction = restriction.strip()
                uri = QgsDataSourceURI()
                user = QSettings().value(SettingsConstants.USER)
                db = QSettings().value(SettingsConstants.DATABASE_NAME)
                host = QSettings().value(SettingsConstants.HOST)
                port = QSettings().value(SettingsConstants.PORT, "5432")
                pwd = SessionHandler().current_password()

                uri.setConnection(host, port, db, user, pwd)
                uri.setDataSource(restriction, layer_name, "geometry", "", id)

                vlayer = QgsVectorLayer(uri.uri(), layer_name, "postgres")
                QgsMapLayerRegistry.instance().addMapLayer(vlayer, False)
                return vlayer

    @staticmethod
    def load_layer_by_ca_sec_parcel(layer_name, id, restrictions=[]):

        restrictions = restrictions.split(",")

        if len(restrictions) > 0:
            for restriction in restrictions:
                restriction = restriction.strip()
                uri = QgsDataSourceURI()
                user = QSettings().value(SettingsConstants.USER)
                db = QSettings().value(SettingsConstants.DATABASE_NAME)
                host = QSettings().value(SettingsConstants.HOST)
                port = QSettings().value(SettingsConstants.PORT, "5432")
                pwd = SessionHandler().current_password()

                uri.setConnection(host, port, db, user, pwd)
                uri.setDataSource("data_landuse", layer_name, "geometry", "", id)

                vlayer = QgsVectorLayer(uri.uri(), layer_name, "postgres")
                QgsMapLayerRegistry.instance().addMapLayer(vlayer, False)
                return vlayer

    @staticmethod
    def load_layer_by_name_pasture_monitoring(layer_name, id):

        uri = QgsDataSourceURI()
        user = QSettings().value(SettingsConstants.USER)
        db = QSettings().value(SettingsConstants.DATABASE_NAME)
        host = QSettings().value(SettingsConstants.HOST)
        port = QSettings().value(SettingsConstants.PORT, "5432")
        pwd = SessionHandler().current_password()

        uri.setConnection(host, port, db, user, pwd)
        uri.setDataSource("pasture", layer_name, "geometry", "", id)

        vlayer = QgsVectorLayer(uri.uri(), layer_name, "postgres")
        QgsMapLayerRegistry.instance().addMapLayer(vlayer, False)
        return vlayer

    @staticmethod
    def load_layer_by_name_set_zones(layer_name, id, restrictions=[]):

        restrictions = restrictions.split(",")

        if len(restrictions) > 0:
            for restriction in restrictions:
                restriction = restriction.strip()
                uri = QgsDataSourceURI()
                user = QSettings().value(SettingsConstants.USER)
                db = QSettings().value(SettingsConstants.DATABASE_NAME)
                host = QSettings().value(SettingsConstants.HOST)
                port = QSettings().value(SettingsConstants.PORT, "5432")
                pwd = SessionHandler().current_password()

                uri.setConnection(host, port, db, user, pwd)
                uri.setDataSource("settings", layer_name, "geometry", "", id)

                vlayer = QgsVectorLayer(uri.uri(), layer_name, "postgres")
                QgsMapLayerRegistry.instance().addMapLayer(vlayer, False)
                return vlayer

    @staticmethod
    def where(layer, exp):

        exp = QgsExpression(exp)

        if exp.hasParserError():
            raise LM2Exception("Error", "Wrong Expression")

        exp.prepare(layer.pendingFields())
        for feature in layer.getFeatures():
            value = exp.evaluate(feature)
            if exp.hasEvalError():
                raise ValueError(exp.evalErrorString())
            if bool(value):
                yield feature

    @staticmethod
    def deselect_all():

        layers = QgsMapLayerRegistry.instance().mapLayers()

        for id, layer in layers.iteritems():
            if layer.type() == QgsMapLayer.VectorLayer:
                layer.removeSelection()

    @staticmethod
    def refresh_layer():

        session = SessionHandler().session_instance()

        root = QgsProject.instance().layerTreeRoot()
        mygroup = root.findGroup(u"Мэдээний хяналт")
        if mygroup is None:
            quality_check_group = root.insertGroup(0, u"Мэдээний хяналт")
        mygroup = root.findGroup(u"ГНСТайлан")
        if mygroup is None:
            gt_report_group = root.insertGroup(1, u"ГНСТайлан")
        mygroup = root.findGroup(u"Тайлан")
        if mygroup is None:
            reports_group = root.insertGroup(2, u"Тайлан")
        mygroup = root.findGroup(u"Кадастрын төлөвлөгөө")
        if mygroup is None:
            cadastre_plan_group = root.insertGroup(3, u"Кадастрын төлөвлөгөө")
        mygroup = root.findGroup(u"Тусгай хамгаалалттай газар")
        if mygroup is None:
            cadastre_plan_group = root.insertGroup(6, u"Тусгай хамгаалалттай газар")
        mygroup = root.findGroup(u"Кадастрын өөрчлөлт")
        if mygroup is None:
            cadastre_maintenance_group = root.insertGroup(2, u"Кадастрын өөрчлөлт")
        mygroup = root.findGroup(u"Кадастр")
        if mygroup is None:
            cadastre_group = root.insertGroup(4, u"Кадастр")
        mygroup = root.findGroup(u"Үнэлгээ, төлбөрийн бүс")
        if mygroup is None:
            land_fee_and_tax_zones_group = root.insertGroup(7, u"Үнэлгээ, төлбөрийн бүс")
        mygroup = root.findGroup(U"Хил")
        if mygroup is None:
            admin_units_group = root.insertGroup(8, u"Хил")
        mygroup = root.findGroup(U"CAMA")
        if mygroup is None:
            admin_units_group = root.insertGroup(8, u"CAMA")

    @staticmethod
    def refresh_layer_plan():

        session = SessionHandler().session_instance()

        root = QgsProject.instance().layerTreeRoot()
        mygroup = root.findGroup(U"ГЗБТөлөвлгөө")
        if mygroup is None:
            plan = root.insertGroup(1, u"ГЗБТөлөвлгөө")
            current_root = plan.insertGroup(1, u"Ажиллаж байгаа")
            current_root.setExpanded(False)
            current_root.insertGroup(1, u"Parcel")
            current_root.insertGroup(2, u"Sub")
            current_root.insertGroup(3, u"Main")

            other_root = plan.insertGroup(2, u"Бусад ГЗБТ")
            other_root.setExpanded(False)
            types = session.query(ClPlanType).order_by(ClPlanType.code.desc()).all()
            count = 1
            for type in types:
                if type.is_point:
                    child_root = other_root.insertGroup(count, type.short_name)
                    child_root.insertGroup(1, u"Parcel")
                    child_root.insertGroup(2, u"Sub")
                    child_root.insertGroup(3, u"Main")
                    child_root.setExpanded(False)
                else:
                    child_root = other_root.insertGroup(count, type.short_name)
                    child_root.insertGroup(1, u"Parcel")
                    child_root.setExpanded(False)
                count += 1