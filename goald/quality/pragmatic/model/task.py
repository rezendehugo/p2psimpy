from goald.quality.pragmatic.model.refinement import Refinement
from goald.quality.pragmatic.model.plan import Plan
from goald.quality.pragmatic.exceptions.metric_not_found import MetricNotFoundException


class Task(Refinement):
    def __init__(self, metric=None, contextValueMap=None, lessIsMore=False, identifier=""):
        Refinement.__init__(self, identifier)
        self.providedQualityLevels = {}
        self.lessIsMore = lessIsMore

        if contextValueMap and metric:
            self.providedQualityLevels[metric] = contextValueMap

    def myType(self):
        return Refinement().TASK

    def setProvidedQuality(self, context, metric, value):
        map = {}

        if metric in self.providedQualityLevels:
            map = self.providedQualityLevels[metric]
            map[context] = value
            self.providedQualityLevels[metric] = map
        else:
            map[context] = value
            self.providedQualityLevels[metric] = map

    def myProvidedQuality(self, metric, contextSet):
        myQuality = 0
        set = False
        if metric not in self.providedQualityLevels:
            raise MetricNotFoundException("Metric: {0}".format(metric.name))

        metricQL = self.providedQualityLevels[metric]

        # getting baseline
        if None in metricQL:
            myQuality = metricQL[None]
            set = True

        for current in contextSet:
            if metric in self.providedQualityLevels:
                if not set:
                    myQuality = metricQL[current]
                    set = True
                else:
                    if metric.getLessIsBetter():
                        if(myQuality > metricQL[current]):
                            myQuality = metricQL[current]
                    elif(myQuality < metricQL[current]):
                        myQuality = metricQL[current]

        return myQuality

    def abidesByInterpretation(self, interp, current):
        feasible = True
        if interp is None:
            return True

        for qc in interp.getQualityConstraints(current):
            try:
                if not qc.abidesByQC(self.myProvidedQuality(qc.metric, current), qc.metric):
                    feasible = False
            except:
                print("MetricNotFoundException Metric: ", qc.metric)
                raise

        if interp.getQualityConstraints(None) is not None:
            for qc in interp.getQualityConstraints(None):
                try:
                    if not qc.abidesByQC(self.myProvidedQuality(qc.getMetric(), current), qc.getMetric()):
                        feasible = False
                except:
                    print("MetricNotFoundException")
                    raise

        return feasible

    def isAchievable(self, current, interp):
        if not self.isApplicable(current):
            return None
        if self.abidesByInterpretation(interp, current):
            return Plan(self)
        else:
            return None
