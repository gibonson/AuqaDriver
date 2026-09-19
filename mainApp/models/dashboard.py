from mainApp import logger
from mainApp.config_operations import load_config_json

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


class DashboardManager:
    def __init__(self):
        self.dashboards = []
        try:
            raw_dashboard_list = load_config_json('dashboard.json')
            for dashboard_data in raw_dashboard_list:
                dashboard = Dashboard(
                    panelType=dashboard_data.get('panelType'),
                    panelItemId=dashboard_data.get('panelItemId'),
                    panelLocation=dashboard_data.get('panelLocation'),
                    panelName=dashboard_data.get('panelName'),
                    panelCode=dashboard_data.get('panelCode'),
                    panelBackground=dashboard_data.get('panelBackground'),
                    panelStatus=dashboard_data.get('panelStatus'),
                )
                self.dashboards.append(dashboard)
        except Exception as e:
            logger.error(f"An error occurred while fetching dashboards: {e}")

    def get_all(self):
        return self.dashboards
    
    def get_ready(self):
        ready = filter(lambda x : x.panelStatus == "Ready", self.dashboards)
        return list(ready)