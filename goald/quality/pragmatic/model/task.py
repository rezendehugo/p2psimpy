from goald.quality.pragmatic.model.refinement import Refinement
from goald.quality.pragmatic.model.plan import Plan
from goald.quality.pragmatic.exceptions.metric_not_found import MetricNotFoundException


class Task(Refinement):
    def __init__(self, identifier):
        Refinement.__init__(self, identifier)
        self.providedQualityLevels = {}
        self.identifier = identifier

    def myType(self):
        return Refinement().TASK
    # Set task provided quality from baseline or context

    def setProvidedQuality(self, context, metric, value):
        metricMap = {}
        # Check if the metric was already in Provided Qualities
        if metric in self.providedQualityLevels:
            metricMap = self.providedQualityLevels[metric]
            metricMap[context] = value
            self.providedQualityLevels[metric] = metricMap
        else:
            metricMap[context] = value
            self.providedQualityLevels[metric] = metricMap

    def myProvidedQuality(self, metric, contextSet):
        myQuality = 0
        initQuality = False
        # Check if the metric was already in Provided Qualities
        if metric not in self.providedQualityLevels.keys():
            message = "Metric: {0} not found".format(metric.name)
            print(message)
            # raise MetricNotFoundException
            return None
        # get metric
        metricQL = self.providedQualityLevels[metric]

        # getting baseline
        if None in metricQL:
            myQuality = metricQL[None]
            initQuality = True
        # test the qualities of active contexts
        for current in contextSet:
            if metricQL.get(current) is None:
                continue
            if not initQuality:
                myQuality = metricQL.get(current)
                initQuality = True
            else:
                # check if less is better for that metric
                if metric.getLessIsBetter():
                    if(myQuality > metricQL[current]):
                        myQuality = metricQL[current]
                elif(myQuality < metricQL[current]):
                    myQuality = metricQL[current]

        return myQuality

    def abidesByInterpretation(self, interp, current):
        # Return if the quality from the task is suitable
        feasible = True
        if interp is None:
            return True

        currentQcs = interp.getQualityConstraints(current)
        # get the qualities constraints from curent contex
        for qc in currentQcs:
            try:
                myQC = self.myProvidedQuality(qc.metric, current)
                if myQC is not None:
                    # check if the metric fits the interpretation constrains
                    if not qc.abidesByQC(myQC, qc.metric):
                        feasible = False
            except MetricNotFoundException:
                pass
        # get the qualities constraints from baseline
        if interp.getQualityConstraints([None]):
            for qc in interp.getQualityConstraints([None]):
                try:
                    myQC = self.myProvidedQuality(qc.metric, current)
                    if myQC is not None:
                        if not qc.abidesByQC(myQC, qc.metric):
                            feasible = False
                except MetricNotFoundException:
                    pass

        return feasible

    def isAchievable(self, current, interp):
        # check if the task is applicable for that context
        if not self.isApplicable(current):
            return None
        # test if quality fit and if return it with Plan to be added
        if self.abidesByInterpretation(interp, current):
            return Plan(self)
        else:
            return None
