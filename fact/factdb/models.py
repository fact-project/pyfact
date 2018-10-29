from peewee import (
    Model,
    FloatField, IntegerField, DateTimeField, CharField, BigIntegerField,
    PrimaryKeyField, CompositeKey
)

from .database import factdata_db

class FactDataModel(Model):
    class Meta:
        database = factdata_db


class AnalysisResultsNightISDC(FactDataModel):
    fnight = IntegerField(column_name='fNight')
    fnumbgevts = FloatField(column_name='fNumBgEvts', null=True)
    fnumevtsafterbgcuts = IntegerField(column_name='fNumEvtsAfterBgCuts', null=True)
    fnumevtsaftercleaning = IntegerField(column_name='fNumEvtsAfterCleaning', null=True)
    fnumevtsafterqualcuts = IntegerField(column_name='fNumEvtsAfterQualCuts', null=True)
    fnumexcevts = FloatField(column_name='fNumExcEvts', null=True)
    fnumislandsmean = FloatField(column_name='fNumIslandsMean', null=True)
    fnumsigevts = FloatField(column_name='fNumSigEvts', null=True)
    fontimeaftercuts = FloatField(column_name='fOnTimeAfterCuts', null=True)
    fsourcekey = IntegerField(column_name='fSourceKey')

    class Meta:
        table_name = 'AnalysisResultsNightISDC'
        indexes = (
            (('fsourcekey', 'fnight'), True),
        )
        primary_key = CompositeKey('fnight', 'fsourcekey')


class AnalysisResultsNightLP(FactDataModel):
    fnight = IntegerField(column_name='fNight')
    fnumbgevts = FloatField(column_name='fNumBgEvts', null=True)
    fnumevtsafterbgcuts = IntegerField(column_name='fNumEvtsAfterBgCuts', null=True)
    fnumevtsaftercleaning = IntegerField(column_name='fNumEvtsAfterCleaning', null=True)
    fnumevtsafterqualcuts = IntegerField(column_name='fNumEvtsAfterQualCuts', null=True)
    fnumexcevts = FloatField(column_name='fNumExcEvts', null=True)
    fnumislandsmean = FloatField(column_name='fNumIslandsMean', null=True)
    fnumsigevts = FloatField(column_name='fNumSigEvts', null=True)
    fontimeaftercuts = FloatField(column_name='fOnTimeAfterCuts', null=True)
    fsourcekey = IntegerField(column_name='fSourceKey')

    class Meta:
        table_name = 'AnalysisResultsNightLP'
        indexes = (
            (('fsourcekey', 'fnight'), True),
        )
        primary_key = CompositeKey('fnight', 'fsourcekey')


class AnalysisResultsRunISDC(FactDataModel):
    flastupdate = DateTimeField(column_name='fLastUpdate')
    fnight = IntegerField(column_name='fNight')
    fnumbgevts = FloatField(column_name='fNumBgEvts', null=True)
    fnumevtsafterantithetacut = FloatField(column_name='fNumEvtsAfterAntiThetaCut')
    fnumevtsafterbgcuts = IntegerField(column_name='fNumEvtsAfterBgCuts', null=True)
    fnumevtsaftercleaning = IntegerField(column_name='fNumEvtsAfterCleaning', null=True)
    fnumevtsafterqualcuts = IntegerField(column_name='fNumEvtsAfterQualCuts', null=True)
    fnumexcevts = FloatField(column_name='fNumExcEvts', null=True)
    fnumislandsmean = FloatField(column_name='fNumIslandsMean', null=True)
    fnumsigevts = FloatField(column_name='fNumSigEvts', null=True)
    fontimeaftercuts = FloatField(column_name='fOnTimeAfterCuts', null=True)
    frunid = IntegerField(column_name='fRunID')

    class Meta:
        table_name = 'AnalysisResultsRunISDC'
        indexes = (
            (('frunid', 'fnight'), True),
        )
        primary_key = CompositeKey('fnight', 'frunid')


class AnalysisResultsRunLP(FactDataModel):
    flastupdate = DateTimeField(column_name='fLastUpdate')
    fnight = IntegerField(column_name='fNight')
    fnumbgevts = FloatField(column_name='fNumBgEvts', null=True)
    fnumevtsafterbgcuts = IntegerField(column_name='fNumEvtsAfterBgCuts', null=True)
    fnumevtsaftercleaning = IntegerField(column_name='fNumEvtsAfterCleaning', null=True)
    fnumevtsafterqualcuts = IntegerField(column_name='fNumEvtsAfterQualCuts', null=True)
    fnumexcevts = FloatField(column_name='fNumExcEvts', null=True)
    fnumislandsmean = FloatField(column_name='fNumIslandsMean', null=True)
    fnumsigevts = FloatField(column_name='fNumSigEvts', null=True)
    fontimeaftercuts = FloatField(column_name='fOnTimeAfterCuts', null=True)
    frunid = IntegerField(column_name='fRunID')

    class Meta:
        table_name = 'AnalysisResultsRunLP'
        indexes = (
            (('frunid', 'fnight'), True),
        )
        primary_key = CompositeKey('fnight', 'frunid')


class AutoSchedule(FactDataModel):
    fdata = CharField(column_name='fData', null=True)
    flastupdate = DateTimeField(column_name='fLastUpdate')
    fmeasurementid = IntegerField(column_name='fMeasurementID')
    fmeasurementtypekey = IntegerField(column_name='fMeasurementTypeKey')
    fscheduleid = PrimaryKeyField(column_name='fScheduleID')
    fsourcekey = IntegerField(column_name='fSourceKey', null=True)
    fstart = DateTimeField(column_name='fStart')
    fuser = CharField(column_name='fUser')

    class Meta:
        table_name = 'AutoSchedule'
        indexes = (
            (('fstart', 'fmeasurementid'), True),
        )


class AuxDataInsertStatus(FactDataModel):
    favailable = DateTimeField(column_name='fAvailable', null=True)
    flastupdate = DateTimeField(column_name='fLastUpdate')
    fnight = PrimaryKeyField(column_name='fNight')
    fpriority = IntegerField(column_name='fPriority')
    fprocessingsitekey = IntegerField(column_name='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(column_name='fReturnCode', null=True)
    fstarttime = DateTimeField(column_name='fStartTime', null=True)
    fstoptime = DateTimeField(column_name='fStopTime', null=True)

    class Meta:
        table_name = 'AuxDataInsertStatus'


class AuxFilesAvailISDCStatus(FactDataModel):
    favailable = DateTimeField(column_name='fAvailable', null=True)
    flastupdate = DateTimeField(column_name='fLastUpdate')
    fnight = PrimaryKeyField(column_name='fNight')
    fpriority = IntegerField(column_name='fPriority')
    fprocessingsitekey = IntegerField(column_name='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(column_name='fReturnCode', null=True)
    fstarttime = DateTimeField(column_name='fStartTime', null=True)
    fstoptime = DateTimeField(column_name='fStopTime', null=True)

    class Meta:
        table_name = 'AuxFilesAvailISDCStatus'


class Calibration(FactDataModel):
    fcaldev = FloatField(column_name='fCalDev', null=True)
    fcalerrdev = FloatField(column_name='fCalErrDev', null=True)
    fcalerrmed = FloatField(column_name='fCalErrMed', null=True)
    fcalmed = FloatField(column_name='fCalMed', null=True)
    fcalvstmdev = FloatField(column_name='fCalVsTmDev', null=True)
    fcalvstmmean = FloatField(column_name='fCalVsTmMean', null=True)
    fcalvstmmed = FloatField(column_name='fCalVsTmMed', null=True)
    fcalvstmrms = FloatField(column_name='fCalVsTmRms', null=True)
    flastupdate = DateTimeField(column_name='fLastUpdate')
    fnight = IntegerField(column_name='fNight')
    fpedextdev = FloatField(column_name='fPedExtDev', null=True)
    fpedexterrdev = FloatField(column_name='fPedExtErrDev', null=True)
    fpedexterrmed = FloatField(column_name='fPedExtErrMed', null=True)
    fpedextmed = FloatField(column_name='fPedExtMed', null=True)
    fpedrndmdev = FloatField(column_name='fPedRndmDev', null=True)
    fpedrndmerrdev = FloatField(column_name='fPedRndmErrDev', null=True)
    fpedrndmerrmed = FloatField(column_name='fPedRndmErrMed', null=True)
    fpedrndmmed = FloatField(column_name='fPedRndmMed', null=True)
    frunstart = DateTimeField(column_name='fRunStart', null=True)
    fsequenceid = IntegerField(column_name='fSequenceID')
    ftmcaldev = FloatField(column_name='fTmCalDev', null=True)
    ftmcalerrdev = FloatField(column_name='fTmCalErrDev', null=True)
    ftmcalerrmed = FloatField(column_name='fTmCalErrMed', null=True)
    ftmcalmed = FloatField(column_name='fTmCalMed', null=True)
    ftmvstmdev = FloatField(column_name='fTmVsTmDev', null=True)
    ftmvstmmean = FloatField(column_name='fTmVsTmMean', null=True)
    ftmvstmmed = FloatField(column_name='fTmVsTmMed', null=True)
    ftmvstmrms = FloatField(column_name='fTmVsTmRms', null=True)
    fzenithdistance = IntegerField(column_name='fZenithDistance', null=True)

    class Meta:
        table_name = 'Calibration'
        indexes = (
            (('fnight', 'fsequenceid'), True),
        )
        primary_key = CompositeKey('fnight', 'fsequenceid')


class CalibrationInfo(FactDataModel):
    flastupdate = DateTimeField(column_name='fLastUpdate')
    fnight = IntegerField(column_name='fNight')
    fsequenceid = IntegerField(column_name='fSequenceID')

    class Meta:
        table_name = 'CalibrationInfo'
        indexes = (
            (('fnight', 'fsequenceid'), True),
        )
        primary_key = CompositeKey('fnight', 'fsequenceid')


class CallistoStatus(FactDataModel):
    favailable = DateTimeField(column_name='fAvailable', null=True)
    flastupdate = DateTimeField(column_name='fLastUpdate')
    fnight = IntegerField(column_name='fNight')
    fpriority = IntegerField(column_name='fPriority')
    fprocessingsitekey = IntegerField(column_name='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(column_name='fReturnCode', null=True)
    fsequenceid = IntegerField(column_name='fSequenceID')
    fstarttime = DateTimeField(column_name='fStartTime', null=True)
    fstoptime = DateTimeField(column_name='fStopTime', null=True)

    class Meta:
        table_name = 'CallistoStatus'
        indexes = (
            (('fnight', 'fsequenceid'), True),
        )
        primary_key = CompositeKey('fnight', 'fsequenceid')


class CallistoWueStatus(FactDataModel):
    favailable = DateTimeField(column_name='fAvailable', null=True)
    flastupdate = DateTimeField(column_name='fLastUpdate')
    fnight = IntegerField(column_name='fNight')
    fpriority = IntegerField(column_name='fPriority')
    fprocessingsitekey = IntegerField(column_name='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(column_name='fReturnCode', null=True)
    fsequenceid = IntegerField(column_name='fSequenceID')
    fstarttime = DateTimeField(column_name='fStartTime', null=True)
    fstoptime = DateTimeField(column_name='fStopTime', null=True)

    class Meta:
        table_name = 'CallistoWueStatus'
        indexes = (
            (('fnight', 'fsequenceid'), True),
        )
        primary_key = CompositeKey('fnight', 'fsequenceid')


class DriveFileAvailISDCStatus(FactDataModel):
    favailable = DateTimeField(column_name='fAvailable', null=True)
    flastupdate = DateTimeField(column_name='fLastUpdate')
    fnight = PrimaryKeyField(column_name='fNight')
    fpriority = IntegerField(column_name='fPriority')
    fprocessingsitekey = IntegerField(column_name='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(column_name='fReturnCode', null=True)
    fstarttime = DateTimeField(column_name='fStartTime', null=True)
    fstoptime = DateTimeField(column_name='fStopTime', null=True)

    class Meta:
        table_name = 'DriveFileAvailISDCStatus'


class DriveFileAvailWueStatus(FactDataModel):
    favailable = DateTimeField(column_name='fAvailable', null=True)
    flastupdate = DateTimeField(column_name='fLastUpdate')
    fnight = PrimaryKeyField(column_name='fNight')
    fpriority = IntegerField(column_name='fPriority')
    fprocessingsitekey = IntegerField(column_name='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(column_name='fReturnCode', null=True)
    fstarttime = DateTimeField(column_name='fStartTime', null=True)
    fstoptime = DateTimeField(column_name='fStopTime', null=True)

    class Meta:
        table_name = 'DriveFileAvailWueStatus'


class ExcludedFDA(FactDataModel):
    fexcludedfda = CharField(column_name='fExcludedFDA', unique=True)
    fexcludedfdakey = PrimaryKeyField(column_name='fExcludedFDAKEY')
    fexcludedfdaname = CharField(column_name='fExcludedFDAName', unique=True)

    class Meta:
        table_name = 'ExcludedFDA'


class FillCalibStatus(FactDataModel):
    favailable = DateTimeField(column_name='fAvailable', null=True)
    flastupdate = DateTimeField(column_name='fLastUpdate')
    fnight = IntegerField(column_name='fNight')
    fpriority = IntegerField(column_name='fPriority')
    fprocessingsitekey = IntegerField(column_name='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(column_name='fReturnCode', null=True)
    fsequenceid = IntegerField(column_name='fSequenceID')
    fstarttime = DateTimeField(column_name='fStartTime', null=True)
    fstoptime = DateTimeField(column_name='fStopTime', null=True)

    class Meta:
        table_name = 'FillCalibStatus'
        indexes = (
            (('fnight', 'fsequenceid'), True),
        )
        primary_key = CompositeKey('fnight', 'fsequenceid')


class FillStarStatus(FactDataModel):
    favailable = DateTimeField(column_name='fAvailable', null=True)
    flastupdate = DateTimeField(column_name='fLastUpdate')
    fnight = IntegerField(column_name='fNight')
    fpriority = IntegerField(column_name='fPriority')
    fprocessingsitekey = IntegerField(column_name='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(column_name='fReturnCode', null=True)
    fsequenceid = IntegerField(column_name='fSequenceID')
    fstarttime = DateTimeField(column_name='fStartTime', null=True)
    fstoptime = DateTimeField(column_name='fStopTime', null=True)

    class Meta:
        table_name = 'FillStarStatus'
        indexes = (
            (('fnight', 'fsequenceid'), True),
        )
        primary_key = CompositeKey('fnight', 'fsequenceid')


class MeasurementType(FactDataModel):
    fisunlimited = IntegerField(column_name='fIsUnlimited')
    fmeasurementtype = CharField(column_name='fMeasurementType')
    fmeasurementtypekey = PrimaryKeyField(column_name='fMeasurementTypeKey')
    fmeasurementtypename = CharField(column_name='fMeasurementTypeName', unique=True)
    fneedssource = IntegerField(column_name='fNeedsSource')

    class Meta:
        table_name = 'MeasurementType'


class ObservationTimes(FactDataModel):
    fmjd = IntegerField(column_name='fMjd')
    fmoonrise = DateTimeField(column_name='fMoonRise')
    fmoonset = DateTimeField(column_name='fMoonSet')
    fnight = PrimaryKeyField(column_name='fNight')
    fnumdarkhours = FloatField(column_name='fNumDarkHours')
    fstartdarknight = DateTimeField(column_name='fStartDarkNight')
    fstartdarktime = DateTimeField(column_name='fStartDarkTime')
    fstartobservation = DateTimeField(column_name='fStartObservation')
    fstopdarknight = DateTimeField(column_name='fStopDarkNight')
    fstopdarktime = DateTimeField(column_name='fStopDarkTime')
    fstopobservation = DateTimeField(column_name='fStopObservation')

    class Meta:
        table_name = 'ObservationTimes'


class Observatory(FactDataModel):
    fmagnetbx = FloatField(column_name='fMagnetBX', null=True)
    fmagnetbz = FloatField(column_name='fMagnetBZ', null=True)
    fmagnetrotation = FloatField(column_name='fMagnetRotation', null=True)
    fobslevel = IntegerField(column_name='fObsLevel')
    fobservatory = CharField(column_name='fObservatory')
    fobservatorykey = PrimaryKeyField(column_name='fObservatoryKEY')
    fobservatoryname = CharField(column_name='fObservatoryName')

    class Meta:
        table_name = 'Observatory'


class RatesFileAvailISDCStatus(FactDataModel):
    favailable = DateTimeField(column_name='fAvailable', null=True)
    flastupdate = DateTimeField(column_name='fLastUpdate')
    fnight = PrimaryKeyField(column_name='fNight')
    fpriority = IntegerField(column_name='fPriority')
    fprocessingsitekey = IntegerField(column_name='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(column_name='fReturnCode', null=True)
    fstarttime = DateTimeField(column_name='fStartTime', null=True)
    fstoptime = DateTimeField(column_name='fStopTime', null=True)

    class Meta:
        table_name = 'RatesFileAvailISDCStatus'


class RatesFileAvailWueStatus(FactDataModel):
    favailable = DateTimeField(column_name='fAvailable', null=True)
    flastupdate = DateTimeField(column_name='fLastUpdate')
    fnight = PrimaryKeyField(column_name='fNight')
    fpriority = IntegerField(column_name='fPriority')
    fprocessingsitekey = IntegerField(column_name='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(column_name='fReturnCode', null=True)
    fstarttime = DateTimeField(column_name='fStartTime', null=True)
    fstoptime = DateTimeField(column_name='fStopTime', null=True)

    class Meta:
        table_name = 'RatesFileAvailWueStatus'


class RateScan(FactDataModel):
    fazmax = FloatField(column_name='fAzMax')
    fazmin = FloatField(column_name='fAzMin')
    fcurrentmedmean = FloatField(column_name='fCurrentMedMean', null=True)
    fdecmean = FloatField(column_name='fDecMean')
    fnight = IntegerField(column_name='fNight')
    fnumpoints = IntegerField(column_name='fNumPoints', null=True)
    fovervoltage = FloatField(column_name='fOvervoltage', null=True)
    framean = FloatField(column_name='fRaMean')
    fratebegin = FloatField(column_name='fRateBegin')
    frateend = FloatField(column_name='fRateEnd')
    fratescanid = PrimaryKeyField(column_name='fRatescanID')
    fthresholdbegin = IntegerField(column_name='fThresholdBegin')
    fthresholdend = IntegerField(column_name='fThresholdEnd')
    ftimebegin = DateTimeField(column_name='fTimeBegin')
    ftimeend = DateTimeField(column_name='fTimeEnd')
    fvoltageison = IntegerField(column_name='fVoltageIsOn', null=True)
    fzdmax = FloatField(column_name='fZdMax')
    fzdmin = FloatField(column_name='fZdMin')

    class Meta:
        table_name = 'Ratescan'


class RawFileAvailISDCStatus(FactDataModel):
    favailable = DateTimeField(column_name='fAvailable', null=True)
    flastupdate = DateTimeField(column_name='fLastUpdate')
    fnight = IntegerField(column_name='fNight')
    fpriority = IntegerField(column_name='fPriority')
    fprocessingsitekey = IntegerField(column_name='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(column_name='fReturnCode', null=True)
    frunid = IntegerField(column_name='fRunID')
    fstarttime = DateTimeField(column_name='fStartTime', null=True)
    fstoptime = DateTimeField(column_name='fStopTime', null=True)

    class Meta:
        table_name = 'RawFileAvailISDCStatus'
        indexes = (
            (('fnight', 'frunid'), True),
        )
        primary_key = CompositeKey('fnight', 'frunid')


class RawFileAvailWueStatus(FactDataModel):
    favailable = DateTimeField(column_name='fAvailable', null=True)
    flastupdate = DateTimeField(column_name='fLastUpdate')
    fnight = IntegerField(column_name='fNight')
    fpriority = IntegerField(column_name='fPriority')
    fprocessingsitekey = IntegerField(column_name='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(column_name='fReturnCode', null=True)
    frunid = IntegerField(column_name='fRunID')
    fstarttime = DateTimeField(column_name='fStartTime', null=True)
    fstoptime = DateTimeField(column_name='fStopTime', null=True)

    class Meta:
        table_name = 'RawFileAvailWueStatus'
        indexes = (
            (('fnight', 'frunid'), True),
        )
        primary_key = CompositeKey('fnight', 'frunid')


class RawfileRsyncedISDCStatus(FactDataModel):
    favailable = DateTimeField(column_name='fAvailable', null=True)
    flastupdate = DateTimeField(column_name='fLastUpdate')
    fnight = IntegerField(column_name='fNight')
    fpriority = IntegerField(column_name='fPriority')
    fprocessingsitekey = IntegerField(column_name='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(column_name='fReturnCode', null=True)
    frunid = IntegerField(column_name='fRunID')
    fstarttime = DateTimeField(column_name='fStartTime', null=True)
    fstoptime = DateTimeField(column_name='fStopTime', null=True)

    class Meta:
        table_name = 'RawFileRsyncedISDCStatus'
        indexes = (
            (('fnight', 'frunid'), True),
        )
        primary_key = CompositeKey('fnight', 'frunid')


class RunComments(FactDataModel):
    fcomment = CharField(column_name='fComment', null=True)
    fcommentkey = PrimaryKeyField(column_name='fCommentKEY')
    fnight = IntegerField(column_name='fNight')
    frunid = IntegerField(column_name='fRunID')
    fuser = CharField(column_name='fUser', null=True)

    class Meta:
        table_name = 'RunComments'


class RunInfo(FactDataModel):
    fangletomoon = FloatField(column_name='fAngleToMoon', null=True)
    fangletosun = FloatField(column_name='fAngleToSun', null=True)
    fazimuthmax = FloatField(column_name='fAzimuthMax', null=True)
    fazimuthmean = FloatField(column_name='fAzimuthMean', null=True)
    fazimuthmin = FloatField(column_name='fAzimuthMin', null=True)
    fbiasvoltagemedian = FloatField(column_name='fBiasVoltageMedian', null=True)
    fcamhumiditymean = FloatField(column_name='fCamHumidityMean', null=True)
    fcameratempmean = FloatField(column_name='fCameraTempMean', null=True)
    fcameratemprms = FloatField(column_name='fCameraTempRms', null=True)
    fcameratemprmsmean = FloatField(column_name='fCameraTempRmsMean', null=True)
    fchecksum = CharField(column_name='fCheckSum', null=True)
    fcompiletime = DateTimeField(column_name='fCompileTime', null=True)
    fcontainertempmean = FloatField(column_name='fContainerTempMean', null=True)
    fctrldevmean = FloatField(column_name='fCtrlDevMean', null=True)
    fctrldevrms = FloatField(column_name='fCtrlDevRms', null=True)
    fcurrentsdevmean = FloatField(column_name='fCurrentsDevMean', null=True)
    fcurrentsdevrms = FloatField(column_name='fCurrentsDevRms', null=True)
    fcurrentsdifftoprediction = FloatField(column_name='fCurrentsDiffToPrediction', null=True)
    fcurrentslinerms = FloatField(column_name='fCurrentsLineRms', null=True)
    fcurrentsmedmean = FloatField(column_name='fCurrentsMedMean', null=True)
    fcurrentsmedmeanbeg = FloatField(column_name='fCurrentsMedMeanBeg', null=True)
    fcurrentsmedmeanend = FloatField(column_name='fCurrentsMedMeanEnd', null=True)
    fcurrentsmedrms = FloatField(column_name='fCurrentsMedRms', null=True)
    fcurrentsreldifftoprediction = FloatField(column_name='fCurrentsRelDiffToPrediction', null=True)
    fcurrentsrellinerms = FloatField(column_name='fCurrentsRelLineRms', null=True)
    fdatasum = CharField(column_name='fDataSum', null=True)
    fdeclination = FloatField(column_name='fDeclination', null=True)
    fdrsstep = IntegerField(column_name='fDrsStep', null=True)
    fdrstempmaxmean = FloatField(column_name='fDrsTempMaxMean', null=True)
    fdrstempmaxrmsmean = FloatField(column_name='fDrsTempMaxRmsMean', null=True)
    fdrstempminmean = FloatField(column_name='fDrsTempMinMean', null=True)
    fdrstempminrmsmean = FloatField(column_name='fDrsTempMinRmsMean', null=True)
    feffectiveon = FloatField(column_name='fEffectiveOn', null=True)
    feffectiveonrms = FloatField(column_name='fEffectiveOnRms', null=True)
    fexcludedfdakey = IntegerField(column_name='fExcludedFDAKEY', null=True)
    ffilesize = BigIntegerField(column_name='fFileSize', null=True)
    ffitsfileerrors = IntegerField(column_name='fFitsFileErrors')
    fhasdrsfile = IntegerField(column_name='fHasDrsFile')
    flastupdate = DateTimeField(column_name='fLastUpdate')
    flidartransmission12 = FloatField(column_name='fLidarTransmission12', null=True)
    flidartransmission3 = FloatField(column_name='fLidarTransmission3', null=True)
    flidartransmission6 = FloatField(column_name='fLidarTransmission6', null=True)
    flidartransmission9 = FloatField(column_name='fLidarTransmission9', null=True)
    fmd5sumraw = CharField(column_name='fMd5sumRaw', null=True)
    fmd5sumrawzip = CharField(column_name='fMd5sumRawZip', null=True)
    fmoondisk = FloatField(column_name='fMoonDisk', null=True)
    fmoonzenithdistance = FloatField(column_name='fMoonZenithDistance', null=True)
    fnight = IntegerField(column_name='fNight')
    fnumelptrigger = IntegerField(column_name='fNumELPTrigger', null=True)
    fnumevents = IntegerField(column_name='fNumEvents', null=True)
    fnumext1trigger = IntegerField(column_name='fNumExt1Trigger', null=True)
    fnumext2trigger = IntegerField(column_name='fNumExt2Trigger', null=True)
    fnumilptrigger = IntegerField(column_name='fNumILPTrigger', null=True)
    fnumothertrigger = IntegerField(column_name='fNumOtherTrigger', null=True)
    fnumpedestaltrigger = IntegerField(column_name='fNumPedestalTrigger', null=True)
    fnumphysicstrigger = IntegerField(column_name='fNumPhysicsTrigger', null=True)
    fnumtimetrigger = IntegerField(column_name='fNumTimeTrigger', null=True)
    fontime = FloatField(column_name='fOnTime', null=True)
    foutsidetempmean = FloatField(column_name='fOutsideTempMean', null=True)
    foutsidetemprms = FloatField(column_name='fOutsideTempRms', null=True)
    fperiod = IntegerField(column_name='fPeriod', null=True)
    froi = IntegerField(column_name='fROI')
    froitimemarker = IntegerField(column_name='fROITimeMarker', null=True)
    frevisionnumber = CharField(column_name='fRevisionNumber', null=True)
    frightascension = FloatField(column_name='fRightAscension', null=True)
    frunid = IntegerField(column_name='fRunID')
    frunstart = DateTimeField(column_name='fRunStart', null=True)
    frunstop = DateTimeField(column_name='fRunStop', null=True)
    fruntypekey = IntegerField(column_name='fRunTypeKey')
    fsequenceid = IntegerField(column_name='fSequenceID', null=True)
    fsourcekey = IntegerField(column_name='fSourceKEY', null=True)
    fsqmmaglinfitchi2 = FloatField(column_name='fSqmMagLinFitChi2', null=True)
    fsqmmaglinfitndf = IntegerField(column_name='fSqmMagLinFitNdf', null=True)
    fsqmmaglinfitpvalue = FloatField(column_name='fSqmMagLinFitPValue', null=True)
    fsqmmaglinfitslope = FloatField(column_name='fSqmMagLinFitSlope', null=True)
    fsqmmagmean = FloatField(column_name='fSqmMagMean', null=True)
    fsunzenithdistance = FloatField(column_name='fSunZenithDistance', null=True)
    ftngdust = FloatField(column_name='fTNGDust', null=True)
    fthresholdavgmean = FloatField(column_name='fThresholdAvgMean', null=True)
    fthresholdmax = IntegerField(column_name='fThresholdMax', null=True)
    fthresholdmedmean = FloatField(column_name='fThresholdMedMean', null=True)
    fthresholdmedrms = FloatField(column_name='fThresholdMedRms', null=True)
    fthresholdmedian = FloatField(column_name='fThresholdMedian', null=True)
    fthresholdminset = IntegerField(column_name='fThresholdMinSet', null=True)
    fthresholdmintimediff = IntegerField(column_name='fThresholdMinTimeDiff', null=True)
    ftriggerratemedian = FloatField(column_name='fTriggerRateMedian', null=True)
    ftriggerraterms = FloatField(column_name='fTriggerRateRms', null=True)
    ftriggerratetimeover100 = FloatField(column_name='fTriggerRateTimeOver100', null=True)
    ftriggerratetimeover125 = FloatField(column_name='fTriggerRateTimeOver125', null=True)
    ftriggerratetimeover150 = FloatField(column_name='fTriggerRateTimeOver150', null=True)
    ftriggerratetimeover175 = FloatField(column_name='fTriggerRateTimeOver175', null=True)
    fzenithdistancemax = FloatField(column_name='fZenithDistanceMax', null=True)
    fzenithdistancemean = FloatField(column_name='fZenithDistanceMean', null=True)
    fzenithdistancemin = FloatField(column_name='fZenithDistanceMin', null=True)

    class Meta:
        table_name = 'RunInfo'
        indexes = (
            (('fnight', 'frunid'), True),
        )
        primary_key = CompositeKey('fnight', 'frunid')


class RunType(FactDataModel):
    fruntype = CharField(column_name='fRunType', unique=True)
    fruntypekey = PrimaryKeyField(column_name='fRunTypeKEY')
    fruntypename = CharField(column_name='fRunTypeName', unique=True)

    class Meta:
        table_name = 'RunType'


class Schedule(FactDataModel):
    fdata = CharField(column_name='fData', null=True)
    flastupdate = DateTimeField(column_name='fLastUpdate')
    fmeasurementid = IntegerField(column_name='fMeasurementID')
    fmeasurementtypekey = IntegerField(column_name='fMeasurementTypeKey')
    fscheduleid = PrimaryKeyField(column_name='fScheduleID')
    fsourcekey = IntegerField(column_name='fSourceKey', null=True)
    fstart = DateTimeField(column_name='fStart')
    fuser = CharField(column_name='fUser')

    class Meta:
        table_name = 'Schedule'
        indexes = (
            (('fstart', 'fmeasurementid'), True),
        )


class SequenceComments(FactDataModel):
    fcomment = CharField(column_name='fComment', null=True)
    fcommentkey = PrimaryKeyField(column_name='fCommentKEY')
    fnight = IntegerField(column_name='fNight')
    fsequenceid = IntegerField(column_name='fSequenceID')
    fuser = CharField(column_name='fUser', null=True)

    class Meta:
        table_name = 'SequenceComments'


class SequenceFileAvailISDCStatus(FactDataModel):
    favailable = DateTimeField(column_name='fAvailable', null=True)
    flastupdate = DateTimeField(column_name='fLastUpdate')
    fnight = IntegerField(column_name='fNight')
    fpriority = IntegerField(column_name='fPriority')
    fprocessingsitekey = IntegerField(column_name='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(column_name='fReturnCode', null=True)
    fsequenceid = IntegerField(column_name='fSequenceID')
    fstarttime = DateTimeField(column_name='fStartTime', null=True)
    fstoptime = DateTimeField(column_name='fStopTime', null=True)

    class Meta:
        table_name = 'SequenceFileAvailISDCStatus'
        indexes = (
            (('fnight', 'fsequenceid'), True),
        )
        primary_key = CompositeKey('fnight', 'fsequenceid')


class SequenceFileAVAILWueStatus(FactDataModel):
    favailable = DateTimeField(column_name='fAvailable', null=True)
    flastupdate = DateTimeField(column_name='fLastUpdate')
    fnight = IntegerField(column_name='fNight')
    fpriority = IntegerField(column_name='fPriority')
    fprocessingsitekey = IntegerField(column_name='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(column_name='fReturnCode', null=True)
    fsequenceid = IntegerField(column_name='fSequenceID')
    fstarttime = DateTimeField(column_name='fStartTime', null=True)
    fstoptime = DateTimeField(column_name='fStopTime', null=True)

    class Meta:
        table_name = 'SequenceFileAvailWueStatus'
        indexes = (
            (('fnight', 'fsequenceid'), True),
        )
        primary_key = CompositeKey('fnight', 'fsequenceid')


class SequenceInfo(FactDataModel):
    fazimuthmax = FloatField(column_name='fAzimuthMax', null=True)
    fazimuthmin = FloatField(column_name='fAzimuthMin', null=True)
    flastupdate = DateTimeField(column_name='fLastUpdate')
    fnight = IntegerField(column_name='fNight')
    fnumevents = IntegerField(column_name='fNumEvents')
    fsequenceduration = IntegerField(column_name='fSequenceDuration')
    fsequenceid = IntegerField(column_name='fSequenceID')
    fsequencestart = DateTimeField(column_name='fSequenceStart')
    fsequencestop = DateTimeField(column_name='fSequenceStop')
    fsourcekey = IntegerField(column_name='fSourceKEY')
    fzenithdistancemax = FloatField(column_name='fZenithDistanceMax', null=True)
    fzenithdistancemin = FloatField(column_name='fZenithDistanceMin', null=True)

    class Meta:
        table_name = 'SequenceInfo'
        indexes = (
            (('fnight', 'fsequenceid'), True),
        )
        primary_key = CompositeKey('fnight', 'fsequenceid')


class Source(FactDataModel):
    fdeclination = FloatField(column_name='fDeclination')
    fepochkey = IntegerField(column_name='fEpochKEY', null=True)
    fflux = FloatField(column_name='fFlux', null=True)
    fistoo = IntegerField(column_name='fIsToO')
    fmagnitude = FloatField(column_name='fMagnitude', null=True)
    frightascension = FloatField(column_name='fRightAscension')
    fslope = FloatField(column_name='fSlope', null=True)
    fsourcekey = PrimaryKeyField(column_name='fSourceKEY')
    fsourcename = CharField(column_name='fSourceName')
    fsourcetypekey = IntegerField(column_name='fSourceTypeKey', index=True)
    fwobbleangle0 = IntegerField(column_name='fWobbleAngle0')
    fwobbleangle1 = IntegerField(column_name='fWobbleAngle1')
    fwobbleoffset = FloatField(column_name='fWobbleOffset')

    class Meta:
        table_name = 'Source'


class SourceType(FactDataModel):
    fsourcetype = CharField(column_name='fSourceType', unique=True)
    fsourcetypekey = PrimaryKeyField(column_name='fSourceTypeKEY')
    fsourcetypename = CharField(column_name='fSourceTypeName', unique=True)

    class Meta:
        table_name = 'SourceType'


class StarInfo(FactDataModel):
    flastupdate = DateTimeField(column_name='fLastUpdate')
    fnight = IntegerField(column_name='fNight')
    fsequenceid = IntegerField(column_name='fSequenceID')

    class Meta:
        table_name = 'StarInfo'
        indexes = (
            (('fnight', 'fsequenceid'), True),
        )
        primary_key = CompositeKey('fnight', 'fsequenceid')


class StarStatus(FactDataModel):
    favailable = DateTimeField(column_name='fAvailable', null=True)
    flastupdate = DateTimeField(column_name='fLastUpdate')
    fnight = IntegerField(column_name='fNight')
    fpriority = IntegerField(column_name='fPriority')
    fprocessingsitekey = IntegerField(column_name='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(column_name='fReturnCode', null=True)
    fsequenceid = IntegerField(column_name='fSequenceID')
    fstarttime = DateTimeField(column_name='fStartTime', null=True)
    fstoptime = DateTimeField(column_name='fStopTime', null=True)

    class Meta:
        table_name = 'StarStatus'
        indexes = (
            (('fnight', 'fsequenceid'), True),
        )
        primary_key = CompositeKey('fnight', 'fsequenceid')


class StarWueStatus(FactDataModel):
    favailable = DateTimeField(column_name='fAvailable', null=True)
    flastupdate = DateTimeField(column_name='fLastUpdate')
    fnight = IntegerField(column_name='fNight')
    fpriority = IntegerField(column_name='fPriority')
    fprocessingsitekey = IntegerField(column_name='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(column_name='fReturnCode', null=True)
    fsequenceid = IntegerField(column_name='fSequenceID')
    fstarttime = DateTimeField(column_name='fStartTime', null=True)
    fstoptime = DateTimeField(column_name='fStopTime', null=True)

    class Meta:
        table_name = 'StarWueStatus'
        indexes = (
            (('fnight', 'fsequenceid'), True),
        )
        primary_key = CompositeKey('fnight', 'fsequenceid')


class TPointData(FactDataModel):
    fazencoder = FloatField(column_name='fAzEncoder')
    fazimage = FloatField(column_name='fAzImage')
    faznominal = FloatField(column_name='fAzNominal')
    fdeclination = FloatField(column_name='fDeclination')
    fintensity = FloatField(column_name='fIntensity')
    fmagcatalog = FloatField(column_name='fMagCatalog')
    fmagmeasured = FloatField(column_name='fMagMeasured')
    fnumleds = IntegerField(column_name='fNumLEDs')
    fnumrings = IntegerField(column_name='fNumRings')
    fqualitykey = IntegerField(column_name='fQualityKEY')
    frightascension = FloatField(column_name='fRightAscension')
    fstarname = CharField(column_name='fStarName')
    ftpointkey = PrimaryKeyField(column_name='fTPointKey')
    ftimestamp = DateTimeField(column_name='fTimeStamp')
    fxposcenter = FloatField(column_name='fXPosCenter')
    fxposstar = FloatField(column_name='fXPosStar')
    fyposcenter = FloatField(column_name='fYPosCenter')
    fyposstar = FloatField(column_name='fYPosStar')
    fzdencoder = FloatField(column_name='fZdEncoder')
    fzdimage = FloatField(column_name='fZdImage')
    fzdnominal = FloatField(column_name='fZdNominal')

    class Meta:
        table_name = 'TPointData'


class TPointQuality(FactDataModel):
    fquality = CharField(column_name='fQuality', null=True, unique=True)
    fqualitykey = PrimaryKeyField(column_name='fQualityKEY')
    fqualityname = CharField(column_name='fQualityName', null=True, unique=True)

    class Meta:
        table_name = 'TPointQuality'
