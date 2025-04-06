from flask_restx import Namespace, Resource, fields, reqparse
from ..models import MetaCampaign, MetaAdSet, MetaAd, MetaInsight
from ..schemas import (
    meta_campaign_schema,
    meta_campaigns_schema,
    meta_ad_set_schema,
    meta_ad_sets_schema,
    meta_ad_schema,
    meta_ads_schema,
    meta_insights_schema,
)

# Namespace para datos relacionados con Meta
meta_ns = Namespace("meta", description="Sincronización y Recuperación de Datos de Meta Ads")

# --- Modelos Reutilizables para Documentación API (Swagger) ---
# Nota: Estos son para documentación, los esquemas Marshmallow manejan la serialización real
campaign_model = meta_ns.model(
    "MetaCampaign",
    {
        "id": fields.String(readonly=True, description="ID de la Campaña"),
        "name": fields.String(description="Nombre de la Campaña"),
        "status": fields.String(description="Estado de la Campaña (ej., ACTIVE, PAUSED)"),
        "effective_status": fields.String(description="Estado Efectivo"),
        "objective": fields.String(description="Objetivo de la Campaña"),
        "created_time": fields.DateTime(description="Marca de Tiempo de Creación"),
        "start_time": fields.DateTime(description="Marca de Tiempo de Inicio"),
        "stop_time": fields.DateTime(description="Marca de Tiempo de Fin"),
        "daily_budget": fields.String(description="Presupuesto Diario"),
        "lifetime_budget": fields.String(description="Presupuesto Total"),
        "budget_remaining": fields.String(description="Presupuesto Restante"),
        "account_id": fields.String(description="ID de la Cuenta Publicitaria"),
    },
)

ad_set_model = meta_ns.model(
    "MetaAdSet",
    {
        "id": fields.String(readonly=True, description="ID del Conjunto de Anuncios"),
        "name": fields.String(description="Nombre del Conjunto de Anuncios"),
        "status": fields.String(description="Estado del Conjunto de Anuncios"),
        "effective_status": fields.String(description="Estado Efectivo"),
        "daily_budget": fields.String(description="Presupuesto Diario"),
        "lifetime_budget": fields.String(description="Presupuesto Total"),
        "budget_remaining": fields.String(description="Presupuesto Restante"),
        "optimization_goal": fields.String(description="Objetivo de Optimización"),
        "billing_event": fields.String(description="Evento de Facturación"),
        "bid_amount": fields.Integer(description="Importe de la Puja"),
        "created_time": fields.DateTime(description="Marca de Tiempo de Creación"),
        "start_time": fields.DateTime(description="Marca de Tiempo de Inicio"),
        "end_time": fields.DateTime(description="Marca de Tiempo de Fin"),
        "campaign_id": fields.String(description="ID de la Campaña Padre"),
    },
)

ad_model = meta_ns.model(
    "MetaAd",
    {
        "id": fields.String(readonly=True, description="ID del Anuncio"),
        "name": fields.String(description="Nombre del Anuncio"),
        "status": fields.String(description="Estado del Anuncio"),
        "effective_status": fields.String(description="Estado Efectivo"),
        "created_time": fields.DateTime(description="Marca de Tiempo de Creación"),
        "creative_id": fields.String(description="ID del Creativo"),
        "creative_details": fields.Raw(
            description="Detalles del Creativo (JSON)"
        ),  # Usar Raw para dict/json
        "ad_set_id": fields.String(description="ID del Conjunto de Anuncios Padre"),
    },
)

insight_model = meta_ns.model(
    "MetaInsight",
    {
        "id": fields.Integer(readonly=True, description="ID del Registro de Insight"),
        "date": fields.Date(description="Fecha del Insight"),
        "impressions": fields.Integer(description="Impresiones"),
        "clicks": fields.Integer(description="Clics"),
        "spend": fields.Float(description="Gasto"),
        "conversions": fields.Integer(description="Conversiones"),
        "cost_per_conversion": fields.Float(description="Costo por Conversión"),
        "submit_applications": fields.Integer(description="Recuento de Envío de Aplicaciones"),
        "submit_applications_value": fields.Float(description="Valor de Envío de Aplicaciones"),
        "leads": fields.Integer(description="Recuento de Leads"),
        "leads_value": fields.Float(description="Valor de Leads"),
        "view_content": fields.Integer(description="Recuento de Vista de Contenido"),
        "view_content_value": fields.Float(description="Valor de Vista de Contenido"),
        "campaign_id": fields.String(description="ID de Campaña Asociada"),
        "ad_set_id": fields.String(description="ID de Conjunto de Anuncios Asociado"),
        "ad_id": fields.String(description="ID de Anuncio Asociado"),
    },
)

# --- Analizadores de Argumentos para Filtrado/Paginación (Opcional pero Recomendado) ---
list_parser = reqparse.RequestParser()
list_parser.add_argument("page", type=int, location="args", default=1, help="Número de página")
list_parser.add_argument(
    "per_page", type=int, location="args", default=20, help="Elementos por página"
)
list_parser.add_argument(
    "account_id", type=str, location="args", help="Filtrar por ID de Cuenta Publicitaria"
)
list_parser.add_argument(
    "status", type=str, location="args", help="Filtrar por estado (ej., ACTIVE)"
)


# --- Recursos de Campaña ---
@meta_ns.route("/campaigns")
class CampaignList(Resource):
    @meta_ns.doc("list_campaigns", parser=list_parser)
    @meta_ns.marshal_list_with(campaign_model)
    def get(self):
        """Listar todas las Campañas de Meta sincronizadas"""
        args = list_parser.parse_args()
        query = MetaCampaign.query

        if args.get("account_id"):
            query = query.filter_by(account_id=args["account_id"])
        if args.get("status"):
            # Filtrado básico, podría mejorarse (ej., insensible a mayúsculas, múltiples estados)
            query = query.filter(MetaCampaign.status.ilike(args["status"]))

        # ¿Excluir eliminados/archivados por defecto a menos que se solicite explícitamente?
        # query = query.filter(MetaCampaign.status.notin_(['DELETED', 'ARCHIVED']))

        pagination = query.paginate(page=args["page"], per_page=args["per_page"], error_out=False)
        return (
            meta_campaigns_schema.dump(pagination.items),
            200,
            {"X-Total-Count": pagination.total},
        )


@meta_ns.route("/campaigns/<string:campaign_id>")
@meta_ns.param("campaign_id", "El identificador de la Campaña de Meta")
@meta_ns.response(404, "Campaña no encontrada")
class CampaignDetail(Resource):
    @meta_ns.doc("get_campaign")
    @meta_ns.marshal_with(campaign_model)
    def get(self, campaign_id):
        """Obtener una única Campaña de Meta por ID"""
        campaign = MetaCampaign.query.get_or_404(campaign_id)
        return meta_campaign_schema.dump(campaign)


# --- Recursos de Conjunto de Anuncios ---
# (Estructura similar: Lista con filtros, Detalle por ID)
@meta_ns.route("/adsets")
class AdSetList(Resource):
    @meta_ns.doc("list_adsets", parser=list_parser)
    @meta_ns.marshal_list_with(ad_set_model)
    def get(self):
        """Listar todos los Conjuntos de Anuncios de Meta sincronizados"""
        args = list_parser.parse_args()
        query = MetaAdSet.query

        if args.get("account_id"):  # Filtrar por cuenta a través de la relación de campaña
            query = query.join(MetaCampaign).filter(MetaCampaign.account_id == args["account_id"])
        if args.get("status"):
            query = query.filter(MetaAdSet.status.ilike(args["status"]))

        pagination = query.paginate(page=args["page"], per_page=args["per_page"], error_out=False)
        return meta_ad_sets_schema.dump(pagination.items), 200, {"X-Total-Count": pagination.total}


@meta_ns.route("/adsets/<string:ad_set_id>")
@meta_ns.param("ad_set_id", "El identificador del Conjunto de Anuncios de Meta")
@meta_ns.response(404, "Conjunto de Anuncios no encontrado")
class AdSetDetail(Resource):
    @meta_ns.doc("get_adset")
    @meta_ns.marshal_with(ad_set_model)
    def get(self, ad_set_id):
        """Obtener un único Conjunto de Anuncios de Meta por ID"""
        ad_set = MetaAdSet.query.get_or_404(ad_set_id)
        return meta_ad_set_schema.dump(ad_set)


# --- Recursos de Anuncio ---
# (Estructura similar)
@meta_ns.route("/ads")
class AdList(Resource):
    @meta_ns.doc("list_ads", parser=list_parser)
    @meta_ns.marshal_list_with(ad_model)
    def get(self):
        """Listar todos los Anuncios de Meta sincronizados"""
        args = list_parser.parse_args()
        query = MetaAd.query

        if args.get(
            "account_id"
        ):  # Filtrar por cuenta a través de la relación campaña/conjunto de anuncios
            query = (
                query.join(MetaAdSet)
                .join(MetaCampaign)
                .filter(MetaCampaign.account_id == args["account_id"])
            )
        if args.get("status"):
            query = query.filter(MetaAd.status.ilike(args["status"]))

        pagination = query.paginate(page=args["page"], per_page=args["per_page"], error_out=False)
        return meta_ads_schema.dump(pagination.items), 200, {"X-Total-Count": pagination.total}


@meta_ns.route("/ads/<string:ad_id>")
@meta_ns.param("ad_id", "El identificador del Anuncio de Meta")
@meta_ns.response(404, "Anuncio no encontrado")
class AdDetail(Resource):
    @meta_ns.doc("get_ad")
    @meta_ns.marshal_with(ad_model)
    def get(self, ad_id):
        """Obtener un único Anuncio de Meta por ID"""
        ad = MetaAd.query.get_or_404(ad_id)
        return meta_ad_schema.dump(ad)


# --- Recursos de Insight ---
# Podría ser necesario un filtrado más complejo aquí (rango de fechas, nivel)
insight_parser = reqparse.RequestParser()
insight_parser.add_argument("page", type=int, location="args", default=1, help="Número de página")
insight_parser.add_argument(
    "per_page", type=int, location="args", default=30, help="Elementos por página"
)
insight_parser.add_argument(
    "account_id", type=str, location="args", help="Filtrar por ID de Cuenta Publicitaria"
)
insight_parser.add_argument(
    "campaign_id", type=str, location="args", help="Filtrar por ID de Campaña"
)
insight_parser.add_argument(
    "ad_set_id", type=str, location="args", help="Filtrar por ID de Conjunto de Anuncios"
)
insight_parser.add_argument("ad_id", type=str, location="args", help="Filtrar por ID de Anuncio")
insight_parser.add_argument(
    "start_date", type=str, location="args", help="Fecha de inicio (YYYY-MM-DD)"
)
insight_parser.add_argument("end_date", type=str, location="args", help="Fecha de fin (YYYY-MM-DD)")


@meta_ns.route("/insights")
class InsightList(Resource):
    @meta_ns.doc("list_insights", parser=insight_parser)
    # ELIMINADO: @meta_ns.marshal_list_with(insight_model) # Esto estaba sobrescribiendo el volcado del esquema
    def get(self):
        """Listar Insights de Meta sincronizados con filtrado"""
        args = insight_parser.parse_args()
        query = MetaInsight.query

        # Filtrado por nivel
        if args.get("ad_id"):
            query = query.filter_by(ad_id=args["ad_id"])
        elif args.get("ad_set_id"):
            query = query.filter_by(ad_set_id=args["ad_set_id"]).filter(MetaInsight.ad_id is None)
        elif args.get("campaign_id"):
            query = (
                query.filter_by(campaign_id=args["campaign_id"])
                .filter(MetaInsight.ad_set_id is None)
                .filter(MetaInsight.ad_id is None)
            )
        elif args.get("account_id"):  # Necesario unir para obtener el ID de la cuenta
            query = query.join(MetaCampaign, MetaInsight.campaign_id == MetaCampaign.id)
            query = query.filter(MetaCampaign.account_id == args["account_id"])
            query = query.filter(MetaInsight.ad_set_id is None).filter(
                MetaInsight.ad_id is None
            )  # Los insights a nivel de cuenta típicamente tienen ids de campaña/conjunto/anuncio nulos

        # Filtrado por fecha
        if args.get("start_date"):
            query = query.filter(MetaInsight.date >= args["start_date"])
        if args.get("end_date"):
            query = query.filter(MetaInsight.date <= args["end_date"])

        # La ordenación predeterminada por fecha podría ser útil
        query = query.order_by(MetaInsight.date_start.desc())

        pagination = query.paginate(page=args["page"], per_page=args["per_page"], error_out=False)
        return meta_insights_schema.dump(pagination.items), 200, {"X-Total-Count": pagination.total}
