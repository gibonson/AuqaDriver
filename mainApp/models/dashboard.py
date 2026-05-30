from mainApp.config_operations import load_json_config
from mainApp import logger

class Dashboard:
    def __init__(
        self,
        panelType,
        panelItemId,
        panelLocation,
        panelName,
        panelCode,
        panelBackground=None,
        panelStatus='Active',
    ):
        self.panelType = panelType
        self.panelItemId = panelItemId
        self.panelLocation = panelLocation
        self.panelName = panelName
        self.panelCode = panelCode
        self.panelBackground = panelBackground
        self.panelStatus = panelStatus


class DashboardLister:
    def __init__(self):
        self.dashboards = []
        try:
            raw_dashboards = load_json_config('dashboards.json', default=[])
            if not isinstance(raw_dashboards, list):
                raw_dashboards = []
            for dashboard_data in raw_dashboards:
                if not isinstance(dashboard_data, dict):
                    continue
                dashboard = Dashboard(
                    panelType=dashboard_data.get('panelType'),
                    panelItemId=dashboard_data.get('panelItemId'),
                    panelLocation=dashboard_data.get('panelLocation'),
                    panelName=dashboard_data.get('panelName'),
                    panelCode=dashboard_data.get('panelCode'),
                    panelBackground=dashboard_data.get('panelBackground'),
                    panelStatus=dashboard_data.get('panelStatus', 'Active'),
                )
                self.dashboards.append(dashboard)
        except Exception as e:
            logger.error(f"An error occurred while fetching dashboards: {e}")

    def get_list(self):
        return self.dashboards
    
