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
    fnight = IntegerField(db_column='fNight')
    fnumbgevts = FloatField(db_column='fNumBgEvts', null=True)
    fnumevtsafterbgcuts = IntegerField(db_column='fNumEvtsAfterBgCuts', null=True)
    fnumevtsaftercleaning = IntegerField(db_column='fNumEvtsAfterCleaning', null=True)
    fnumevtsafterqualcuts = IntegerField(db_column='fNumEvtsAfterQualCuts', null=True)
    fnumexcevts = FloatField(db_column='fNumExcEvts', null=True)
    fnumislandsmean = FloatField(db_column='fNumIslandsMean', null=True)
    fnumsigevts = FloatField(db_column='fNumSigEvts', null=True)
    fontimeaftercuts = FloatField(db_column='fOnTimeAfterCuts', null=True)
    fsourcekey = IntegerField(db_column='fSourceKey')

    class Meta:
        db_table = 'AnalysisResultsNightISDC'
        indexes = (
            (('fsourcekey', 'fnight'), True),
        )
        primary_key = CompositeKey('fnight', 'fsourcekey')


class AnalysisResultsNightLP(FactDataModel):
    fnight = IntegerField(db_column='fNight')
    fnumbgevts = FloatField(db_column='fNumBgEvts', null=True)
    fnumevtsafterbgcuts = IntegerField(db_column='fNumEvtsAfterBgCuts', null=True)
    fnumevtsaftercleaning = IntegerField(db_column='fNumEvtsAfterCleaning', null=True)
    fnumevtsafterqualcuts = IntegerField(db_column='fNumEvtsAfterQualCuts', null=True)
    fnumexcevts = FloatField(db_column='fNumExcEvts', null=True)
    fnumislandsmean = FloatField(db_column='fNumIslandsMean', null=True)
    fnumsigevts = FloatField(db_column='fNumSigEvts', null=True)
    fontimeaftercuts = FloatField(db_column='fOnTimeAfterCuts', null=True)
    fsourcekey = IntegerField(db_column='fSourceKey')

    class Meta:
        db_table = 'AnalysisResultsNightLP'
        indexes = (
            (('fsourcekey', 'fnight'), True),
        )
        primary_key = CompositeKey('fnight', 'fsourcekey')


class AnalysisResultsRunISDC(FactDataModel):
    flastupdate = DateTimeField(db_column='fLastUpdate')
    fnight = IntegerField(db_column='fNight')
    fnumbgevts = FloatField(db_column='fNumBgEvts', null=True)
    fnumevtsafterantithetacut = FloatField(db_column='fNumEvtsAfterAntiThetaCut')
    fnumevtsafterbgcuts = IntegerField(db_column='fNumEvtsAfterBgCuts', null=True)
    fnumevtsaftercleaning = IntegerField(db_column='fNumEvtsAfterCleaning', null=True)
    fnumevtsafterqualcuts = IntegerField(db_column='fNumEvtsAfterQualCuts', null=True)
    fnumexcevts = FloatField(db_column='fNumExcEvts', null=True)
    fnumislandsmean = FloatField(db_column='fNumIslandsMean', null=True)
    fnumsigevts = FloatField(db_column='fNumSigEvts', null=True)
    fontimeaftercuts = FloatField(db_column='fOnTimeAfterCuts', null=True)
    frunid = IntegerField(db_column='fRunID')

    class Meta:
        db_table = 'AnalysisResultsRunISDC'
        indexes = (
            (('frunid', 'fnight'), True),
        )
        primary_key = CompositeKey('fnight', 'frunid')


class AnalysisResultsRunLP(FactDataModel):
    flastupdate = DateTimeField(db_column='fLastUpdate')
    fnight = IntegerField(db_column='fNight')
    fnumbgevts = FloatField(db_column='fNumBgEvts', null=True)
    fnumevtsafterbgcuts = IntegerField(db_column='fNumEvtsAfterBgCuts', null=True)
    fnumevtsaftercleaning = IntegerField(db_column='fNumEvtsAfterCleaning', null=True)
    fnumevtsafterqualcuts = IntegerField(db_column='fNumEvtsAfterQualCuts', null=True)
    fnumexcevts = FloatField(db_column='fNumExcEvts', null=True)
    fnumislandsmean = FloatField(db_column='fNumIslandsMean', null=True)
    fnumsigevts = FloatField(db_column='fNumSigEvts', null=True)
    fontimeaftercuts = FloatField(db_column='fOnTimeAfterCuts', null=True)
    frunid = IntegerField(db_column='fRunID')

    class Meta:
        db_table = 'AnalysisResultsRunLP'
        indexes = (
            (('frunid', 'fnight'), True),
        )
        primary_key = CompositeKey('fnight', 'frunid')


class AutoSchedule(FactDataModel):
    fdata = CharField(db_column='fData', null=True)
    flastupdate = DateTimeField(db_column='fLastUpdate')
    fmeasurementid = IntegerField(db_column='fMeasurementID')
    fmeasurementtypekey = IntegerField(db_column='fMeasurementTypeKey')
    fscheduleid = PrimaryKeyField(db_column='fScheduleID')
    fsourcekey = IntegerField(db_column='fSourceKey', null=True)
    fstart = DateTimeField(db_column='fStart')
    fuser = CharField(db_column='fUser')

    class Meta:
        db_table = 'AutoSchedule'
        indexes = (
            (('fstart', 'fmeasurementid'), True),
        )


class AuxDataInsertStatus(FactDataModel):
    favailable = DateTimeField(db_column='fAvailable', null=True)
    flastupdate = DateTimeField(db_column='fLastUpdate')
    fnight = PrimaryKeyField(db_column='fNight')
    fpriority = IntegerField(db_column='fPriority')
    fprocessingsitekey = IntegerField(db_column='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(db_column='fReturnCode', null=True)
    fstarttime = DateTimeField(db_column='fStartTime', null=True)
    fstoptime = DateTimeField(db_column='fStopTime', null=True)

    class Meta:
        db_table = 'AuxDataInsertStatus'


class AuxFilesAvailISDCStatus(FactDataModel):
    favailable = DateTimeField(db_column='fAvailable', null=True)
    flastupdate = DateTimeField(db_column='fLastUpdate')
    fnight = PrimaryKeyField(db_column='fNight')
    fpriority = IntegerField(db_column='fPriority')
    fprocessingsitekey = IntegerField(db_column='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(db_column='fReturnCode', null=True)
    fstarttime = DateTimeField(db_column='fStartTime', null=True)
    fstoptime = DateTimeField(db_column='fStopTime', null=True)

    class Meta:
        db_table = 'AuxFilesAvailISDCStatus'


class Calibration(FactDataModel):
    fcaldev = FloatField(db_column='fCalDev', null=True)
    fcalerrdev = FloatField(db_column='fCalErrDev', null=True)
    fcalerrmed = FloatField(db_column='fCalErrMed', null=True)
    fcalmed = FloatField(db_column='fCalMed', null=True)
    fcalvstmdev = FloatField(db_column='fCalVsTmDev', null=True)
    fcalvstmmean = FloatField(db_column='fCalVsTmMean', null=True)
    fcalvstmmed = FloatField(db_column='fCalVsTmMed', null=True)
    fcalvstmrms = FloatField(db_column='fCalVsTmRms', null=True)
    flastupdate = DateTimeField(db_column='fLastUpdate')
    fnight = IntegerField(db_column='fNight')
    fpedextdev = FloatField(db_column='fPedExtDev', null=True)
    fpedexterrdev = FloatField(db_column='fPedExtErrDev', null=True)
    fpedexterrmed = FloatField(db_column='fPedExtErrMed', null=True)
    fpedextmed = FloatField(db_column='fPedExtMed', null=True)
    fpedrndmdev = FloatField(db_column='fPedRndmDev', null=True)
    fpedrndmerrdev = FloatField(db_column='fPedRndmErrDev', null=True)
    fpedrndmerrmed = FloatField(db_column='fPedRndmErrMed', null=True)
    fpedrndmmed = FloatField(db_column='fPedRndmMed', null=True)
    frunstart = DateTimeField(db_column='fRunStart', null=True)
    fsequenceid = IntegerField(db_column='fSequenceID')
    ftmcaldev = FloatField(db_column='fTmCalDev', null=True)
    ftmcalerrdev = FloatField(db_column='fTmCalErrDev', null=True)
    ftmcalerrmed = FloatField(db_column='fTmCalErrMed', null=True)
    ftmcalmed = FloatField(db_column='fTmCalMed', null=True)
    ftmvstmdev = FloatField(db_column='fTmVsTmDev', null=True)
    ftmvstmmean = FloatField(db_column='fTmVsTmMean', null=True)
    ftmvstmmed = FloatField(db_column='fTmVsTmMed', null=True)
    ftmvstmrms = FloatField(db_column='fTmVsTmRms', null=True)
    fzenithdistance = IntegerField(db_column='fZenithDistance', null=True)

    class Meta:
        db_table = 'Calibration'
        indexes = (
            (('fnight', 'fsequenceid'), True),
        )
        primary_key = CompositeKey('fnight', 'fsequenceid')


class CalibrationInfo(FactDataModel):
    flastupdate = DateTimeField(db_column='fLastUpdate')
    fnight = IntegerField(db_column='fNight')
    fsequenceid = IntegerField(db_column='fSequenceID')

    class Meta:
        db_table = 'CalibrationInfo'
        indexes = (
            (('fnight', 'fsequenceid'), True),
        )
        primary_key = CompositeKey('fnight', 'fsequenceid')


class CallistoStatus(FactDataModel):
    favailable = DateTimeField(db_column='fAvailable', null=True)
    flastupdate = DateTimeField(db_column='fLastUpdate')
    fnight = IntegerField(db_column='fNight')
    fpriority = IntegerField(db_column='fPriority')
    fprocessingsitekey = IntegerField(db_column='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(db_column='fReturnCode', null=True)
    fsequenceid = IntegerField(db_column='fSequenceID')
    fstarttime = DateTimeField(db_column='fStartTime', null=True)
    fstoptime = DateTimeField(db_column='fStopTime', null=True)

    class Meta:
        db_table = 'CallistoStatus'
        indexes = (
            (('fnight', 'fsequenceid'), True),
        )
        primary_key = CompositeKey('fnight', 'fsequenceid')


class CallistoWueStatus(FactDataModel):
    favailable = DateTimeField(db_column='fAvailable', null=True)
    flastupdate = DateTimeField(db_column='fLastUpdate')
    fnight = IntegerField(db_column='fNight')
    fpriority = IntegerField(db_column='fPriority')
    fprocessingsitekey = IntegerField(db_column='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(db_column='fReturnCode', null=True)
    fsequenceid = IntegerField(db_column='fSequenceID')
    fstarttime = DateTimeField(db_column='fStartTime', null=True)
    fstoptime = DateTimeField(db_column='fStopTime', null=True)

    class Meta:
        db_table = 'CallistoWueStatus'
        indexes = (
            (('fnight', 'fsequenceid'), True),
        )
        primary_key = CompositeKey('fnight', 'fsequenceid')


class DriveFileAvailISDCStatus(FactDataModel):
    favailable = DateTimeField(db_column='fAvailable', null=True)
    flastupdate = DateTimeField(db_column='fLastUpdate')
    fnight = PrimaryKeyField(db_column='fNight')
    fpriority = IntegerField(db_column='fPriority')
    fprocessingsitekey = IntegerField(db_column='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(db_column='fReturnCode', null=True)
    fstarttime = DateTimeField(db_column='fStartTime', null=True)
    fstoptime = DateTimeField(db_column='fStopTime', null=True)

    class Meta:
        db_table = 'DriveFileAvailISDCStatus'


class DriveFileAvailWueStatus(FactDataModel):
    favailable = DateTimeField(db_column='fAvailable', null=True)
    flastupdate = DateTimeField(db_column='fLastUpdate')
    fnight = PrimaryKeyField(db_column='fNight')
    fpriority = IntegerField(db_column='fPriority')
    fprocessingsitekey = IntegerField(db_column='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(db_column='fReturnCode', null=True)
    fstarttime = DateTimeField(db_column='fStartTime', null=True)
    fstoptime = DateTimeField(db_column='fStopTime', null=True)

    class Meta:
        db_table = 'DriveFileAvailWueStatus'


class ExcludedFDA(FactDataModel):
    fexcludedfda = CharField(db_column='fExcludedFDA', unique=True)
    fexcludedfdakey = PrimaryKeyField(db_column='fExcludedFDAKEY')
    fexcludedfdaname = CharField(db_column='fExcludedFDAName', unique=True)

    class Meta:
        db_table = 'ExcludedFDA'


class FillCalibStatus(FactDataModel):
    favailable = DateTimeField(db_column='fAvailable', null=True)
    flastupdate = DateTimeField(db_column='fLastUpdate')
    fnight = IntegerField(db_column='fNight')
    fpriority = IntegerField(db_column='fPriority')
    fprocessingsitekey = IntegerField(db_column='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(db_column='fReturnCode', null=True)
    fsequenceid = IntegerField(db_column='fSequenceID')
    fstarttime = DateTimeField(db_column='fStartTime', null=True)
    fstoptime = DateTimeField(db_column='fStopTime', null=True)

    class Meta:
        db_table = 'FillCalibStatus'
        indexes = (
            (('fnight', 'fsequenceid'), True),
        )
        primary_key = CompositeKey('fnight', 'fsequenceid')


class FillStarStatus(FactDataModel):
    favailable = DateTimeField(db_column='fAvailable', null=True)
    flastupdate = DateTimeField(db_column='fLastUpdate')
    fnight = IntegerField(db_column='fNight')
    fpriority = IntegerField(db_column='fPriority')
    fprocessingsitekey = IntegerField(db_column='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(db_column='fReturnCode', null=True)
    fsequenceid = IntegerField(db_column='fSequenceID')
    fstarttime = DateTimeField(db_column='fStartTime', null=True)
    fstoptime = DateTimeField(db_column='fStopTime', null=True)

    class Meta:
        db_table = 'FillStarStatus'
        indexes = (
            (('fnight', 'fsequenceid'), True),
        )
        primary_key = CompositeKey('fnight', 'fsequenceid')


class MeasurementType(FactDataModel):
    fisunlimited = IntegerField(db_column='fIsUnlimited')
    fmeasurementtype = CharField(db_column='fMeasurementType')
    fmeasurementtypekey = PrimaryKeyField(db_column='fMeasurementTypeKey')
    fmeasurementtypename = CharField(db_column='fMeasurementTypeName', unique=True)
    fneedssource = IntegerField(db_column='fNeedsSource')

    class Meta:
        db_table = 'MeasurementType'


class ObservationTimes(FactDataModel):
    fmjd = IntegerField(db_column='fMjd')
    fmoonrise = DateTimeField(db_column='fMoonRise')
    fmoonset = DateTimeField(db_column='fMoonSet')
    fnight = PrimaryKeyField(db_column='fNight')
    fnumdarkhours = FloatField(db_column='fNumDarkHours')
    fstartdarknight = DateTimeField(db_column='fStartDarkNight')
    fstartdarktime = DateTimeField(db_column='fStartDarkTime')
    fstartobservation = DateTimeField(db_column='fStartObservation')
    fstopdarknight = DateTimeField(db_column='fStopDarkNight')
    fstopdarktime = DateTimeField(db_column='fStopDarkTime')
    fstopobservation = DateTimeField(db_column='fStopObservation')

    class Meta:
        db_table = 'ObservationTimes'


class Observatory(FactDataModel):
    fmagnetbx = FloatField(db_column='fMagnetBX', null=True)
    fmagnetbz = FloatField(db_column='fMagnetBZ', null=True)
    fmagnetrotation = FloatField(db_column='fMagnetRotation', null=True)
    fobslevel = IntegerField(db_column='fObsLevel')
    fobservatory = CharField(db_column='fObservatory')
    fobservatorykey = PrimaryKeyField(db_column='fObservatoryKEY')
    fobservatoryname = CharField(db_column='fObservatoryName')

    class Meta:
        db_table = 'Observatory'


class RatesFileAvailISDCStatus(FactDataModel):
    favailable = DateTimeField(db_column='fAvailable', null=True)
    flastupdate = DateTimeField(db_column='fLastUpdate')
    fnight = PrimaryKeyField(db_column='fNight')
    fpriority = IntegerField(db_column='fPriority')
    fprocessingsitekey = IntegerField(db_column='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(db_column='fReturnCode', null=True)
    fstarttime = DateTimeField(db_column='fStartTime', null=True)
    fstoptime = DateTimeField(db_column='fStopTime', null=True)

    class Meta:
        db_table = 'RatesFileAvailISDCStatus'


class RatesFileAvailWueStatus(FactDataModel):
    favailable = DateTimeField(db_column='fAvailable', null=True)
    flastupdate = DateTimeField(db_column='fLastUpdate')
    fnight = PrimaryKeyField(db_column='fNight')
    fpriority = IntegerField(db_column='fPriority')
    fprocessingsitekey = IntegerField(db_column='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(db_column='fReturnCode', null=True)
    fstarttime = DateTimeField(db_column='fStartTime', null=True)
    fstoptime = DateTimeField(db_column='fStopTime', null=True)

    class Meta:
        db_table = 'RatesFileAvailWueStatus'


class RateScan(FactDataModel):
    fazmax = FloatField(db_column='fAzMax')
    fazmin = FloatField(db_column='fAzMin')
    fcurrentmedmean = FloatField(db_column='fCurrentMedMean', null=True)
    fdecmean = FloatField(db_column='fDecMean')
    fnight = IntegerField(db_column='fNight')
    fnumpoints = IntegerField(db_column='fNumPoints', null=True)
    fovervoltage = FloatField(db_column='fOvervoltage', null=True)
    framean = FloatField(db_column='fRaMean')
    fratebegin = FloatField(db_column='fRateBegin')
    frateend = FloatField(db_column='fRateEnd')
    fratescanid = PrimaryKeyField(db_column='fRatescanID')
    fthresholdbegin = IntegerField(db_column='fThresholdBegin')
    fthresholdend = IntegerField(db_column='fThresholdEnd')
    ftimebegin = DateTimeField(db_column='fTimeBegin')
    ftimeend = DateTimeField(db_column='fTimeEnd')
    fvoltageison = IntegerField(db_column='fVoltageIsOn', null=True)
    fzdmax = FloatField(db_column='fZdMax')
    fzdmin = FloatField(db_column='fZdMin')

    class Meta:
        db_table = 'Ratescan'


class RawFileAvailISDCStatus(FactDataModel):
    favailable = DateTimeField(db_column='fAvailable', null=True)
    flastupdate = DateTimeField(db_column='fLastUpdate')
    fnight = IntegerField(db_column='fNight')
    fpriority = IntegerField(db_column='fPriority')
    fprocessingsitekey = IntegerField(db_column='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(db_column='fReturnCode', null=True)
    frunid = IntegerField(db_column='fRunID')
    fstarttime = DateTimeField(db_column='fStartTime', null=True)
    fstoptime = DateTimeField(db_column='fStopTime', null=True)

    class Meta:
        db_table = 'RawFileAvailISDCStatus'
        indexes = (
            (('fnight', 'frunid'), True),
        )
        primary_key = CompositeKey('fnight', 'frunid')


class RawFileAvailWueStatus(FactDataModel):
    favailable = DateTimeField(db_column='fAvailable', null=True)
    flastupdate = DateTimeField(db_column='fLastUpdate')
    fnight = IntegerField(db_column='fNight')
    fpriority = IntegerField(db_column='fPriority')
    fprocessingsitekey = IntegerField(db_column='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(db_column='fReturnCode', null=True)
    frunid = IntegerField(db_column='fRunID')
    fstarttime = DateTimeField(db_column='fStartTime', null=True)
    fstoptime = DateTimeField(db_column='fStopTime', null=True)

    class Meta:
        db_table = 'RawFileAvailWueStatus'
        indexes = (
            (('fnight', 'frunid'), True),
        )
        primary_key = CompositeKey('fnight', 'frunid')


class RawfileRsyncedISDCStatus(FactDataModel):
    favailable = DateTimeField(db_column='fAvailable', null=True)
    flastupdate = DateTimeField(db_column='fLastUpdate')
    fnight = IntegerField(db_column='fNight')
    fpriority = IntegerField(db_column='fPriority')
    fprocessingsitekey = IntegerField(db_column='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(db_column='fReturnCode', null=True)
    frunid = IntegerField(db_column='fRunID')
    fstarttime = DateTimeField(db_column='fStartTime', null=True)
    fstoptime = DateTimeField(db_column='fStopTime', null=True)

    class Meta:
        db_table = 'RawFileRsyncedISDCStatus'
        indexes = (
            (('fnight', 'frunid'), True),
        )
        primary_key = CompositeKey('fnight', 'frunid')


class RunComments(FactDataModel):
    fcomment = CharField(db_column='fComment', null=True)
    fcommentkey = PrimaryKeyField(db_column='fCommentKEY')
    fnight = IntegerField(db_column='fNight')
    frunid = IntegerField(db_column='fRunID')
    fuser = CharField(db_column='fUser', null=True)

    class Meta:
        db_table = 'RunComments'


class RunInfo(FactDataModel):
    fangletomoon = FloatField(db_column='fAngleToMoon', null=True)
    fangletosun = FloatField(db_column='fAngleToSun', null=True)
    fazimuthmax = FloatField(db_column='fAzimuthMax', null=True)
    fazimuthmean = FloatField(db_column='fAzimuthMean', null=True)
    fazimuthmin = FloatField(db_column='fAzimuthMin', null=True)
    fbiasvoltagemedian = FloatField(db_column='fBiasVoltageMedian', null=True)
    fcamhumiditymean = FloatField(db_column='fCamHumidityMean', null=True)
    fcameratempmean = FloatField(db_column='fCameraTempMean', null=True)
    fcameratemprms = FloatField(db_column='fCameraTempRms', null=True)
    fcameratemprmsmean = FloatField(db_column='fCameraTempRmsMean', null=True)
    fchecksum = CharField(db_column='fCheckSum', null=True)
    fcompiletime = DateTimeField(db_column='fCompileTime', null=True)
    fcontainertempmean = FloatField(db_column='fContainerTempMean', null=True)
    fctrldevmean = FloatField(db_column='fCtrlDevMean', null=True)
    fctrldevrms = FloatField(db_column='fCtrlDevRms', null=True)
    fcurrentsdevmean = FloatField(db_column='fCurrentsDevMean', null=True)
    fcurrentsdevrms = FloatField(db_column='fCurrentsDevRms', null=True)
    fcurrentsdifftoprediction = FloatField(db_column='fCurrentsDiffToPrediction', null=True)
    fcurrentslinerms = FloatField(db_column='fCurrentsLineRms', null=True)
    fcurrentsmedmean = FloatField(db_column='fCurrentsMedMean', null=True)
    fcurrentsmedmeanbeg = FloatField(db_column='fCurrentsMedMeanBeg', null=True)
    fcurrentsmedmeanend = FloatField(db_column='fCurrentsMedMeanEnd', null=True)
    fcurrentsmedrms = FloatField(db_column='fCurrentsMedRms', null=True)
    fcurrentsreldifftoprediction = FloatField(db_column='fCurrentsRelDiffToPrediction', null=True)
    fcurrentsrellinerms = FloatField(db_column='fCurrentsRelLineRms', null=True)
    fdatasum = CharField(db_column='fDataSum', null=True)
    fdeclination = FloatField(db_column='fDeclination', null=True)
    fdrsstep = IntegerField(db_column='fDrsStep', null=True)
    fdrstempmaxmean = FloatField(db_column='fDrsTempMaxMean', null=True)
    fdrstempmaxrmsmean = FloatField(db_column='fDrsTempMaxRmsMean', null=True)
    fdrstempminmean = FloatField(db_column='fDrsTempMinMean', null=True)
    fdrstempminrmsmean = FloatField(db_column='fDrsTempMinRmsMean', null=True)
    feffectiveon = FloatField(db_column='fEffectiveOn', null=True)
    feffectiveonrms = FloatField(db_column='fEffectiveOnRms', null=True)
    fexcludedfdakey = IntegerField(db_column='fExcludedFDAKEY', null=True)
    ffilesize = BigIntegerField(db_column='fFileSize', null=True)
    ffitsfileerrors = IntegerField(db_column='fFitsFileErrors')
    fhasdrsfile = IntegerField(db_column='fHasDrsFile')
    flastupdate = DateTimeField(db_column='fLastUpdate')
    flidartransmission12 = FloatField(db_column='fLidarTransmission12', null=True)
    flidartransmission3 = FloatField(db_column='fLidarTransmission3', null=True)
    flidartransmission6 = FloatField(db_column='fLidarTransmission6', null=True)
    flidartransmission9 = FloatField(db_column='fLidarTransmission9', null=True)
    fmd5sumraw = CharField(db_column='fMd5sumRaw', null=True)
    fmd5sumrawzip = CharField(db_column='fMd5sumRawZip', null=True)
    fmoondisk = FloatField(db_column='fMoonDisk', null=True)
    fmoonzenithdistance = FloatField(db_column='fMoonZenithDistance', null=True)
    fnight = IntegerField(db_column='fNight')
    fnumelptrigger = IntegerField(db_column='fNumELPTrigger', null=True)
    fnumevents = IntegerField(db_column='fNumEvents', null=True)
    fnumext1trigger = IntegerField(db_column='fNumExt1Trigger', null=True)
    fnumext2trigger = IntegerField(db_column='fNumExt2Trigger', null=True)
    fnumilptrigger = IntegerField(db_column='fNumILPTrigger', null=True)
    fnumothertrigger = IntegerField(db_column='fNumOtherTrigger', null=True)
    fnumpedestaltrigger = IntegerField(db_column='fNumPedestalTrigger', null=True)
    fnumphysicstrigger = IntegerField(db_column='fNumPhysicsTrigger', null=True)
    fnumtimetrigger = IntegerField(db_column='fNumTimeTrigger', null=True)
    fontime = FloatField(db_column='fOnTime', null=True)
    foutsidetempmean = FloatField(db_column='fOutsideTempMean', null=True)
    foutsidetemprms = FloatField(db_column='fOutsideTempRms', null=True)
    fperiod = IntegerField(db_column='fPeriod', null=True)
    froi = IntegerField(db_column='fROI')
    froitimemarker = IntegerField(db_column='fROITimeMarker', null=True)
    frevisionnumber = CharField(db_column='fRevisionNumber', null=True)
    frightascension = FloatField(db_column='fRightAscension', null=True)
    frunid = IntegerField(db_column='fRunID')
    frunstart = DateTimeField(db_column='fRunStart', null=True)
    frunstop = DateTimeField(db_column='fRunStop', null=True)
    fruntypekey = IntegerField(db_column='fRunTypeKey')
    fsequenceid = IntegerField(db_column='fSequenceID', null=True)
    fsourcekey = IntegerField(db_column='fSourceKEY', null=True)
    fsqmmaglinfitchi2 = FloatField(db_column='fSqmMagLinFitChi2', null=True)
    fsqmmaglinfitndf = IntegerField(db_column='fSqmMagLinFitNdf', null=True)
    fsqmmaglinfitpvalue = FloatField(db_column='fSqmMagLinFitPValue', null=True)
    fsqmmaglinfitslope = FloatField(db_column='fSqmMagLinFitSlope', null=True)
    fsqmmagmean = FloatField(db_column='fSqmMagMean', null=True)
    fsunzenithdistance = FloatField(db_column='fSunZenithDistance', null=True)
    ftngdust = FloatField(db_column='fTNGDust', null=True)
    fthresholdavgmean = FloatField(db_column='fThresholdAvgMean', null=True)
    fthresholdmax = IntegerField(db_column='fThresholdMax', null=True)
    fthresholdmedmean = FloatField(db_column='fThresholdMedMean', null=True)
    fthresholdmedrms = FloatField(db_column='fThresholdMedRms', null=True)
    fthresholdmedian = FloatField(db_column='fThresholdMedian', null=True)
    fthresholdminset = IntegerField(db_column='fThresholdMinSet', null=True)
    fthresholdmintimediff = IntegerField(db_column='fThresholdMinTimeDiff', null=True)
    ftriggerratemedian = FloatField(db_column='fTriggerRateMedian', null=True)
    ftriggerraterms = FloatField(db_column='fTriggerRateRms', null=True)
    ftriggerratetimeover100 = FloatField(db_column='fTriggerRateTimeOver100', null=True)
    ftriggerratetimeover125 = FloatField(db_column='fTriggerRateTimeOver125', null=True)
    ftriggerratetimeover150 = FloatField(db_column='fTriggerRateTimeOver150', null=True)
    ftriggerratetimeover175 = FloatField(db_column='fTriggerRateTimeOver175', null=True)
    fzenithdistancemax = FloatField(db_column='fZenithDistanceMax', null=True)
    fzenithdistancemean = FloatField(db_column='fZenithDistanceMean', null=True)
    fzenithdistancemin = FloatField(db_column='fZenithDistanceMin', null=True)

    class Meta:
        db_table = 'RunInfo'
        indexes = (
            (('fnight', 'frunid'), True),
        )
        primary_key = CompositeKey('fnight', 'frunid')


class RunType(FactDataModel):
    fruntype = CharField(db_column='fRunType', unique=True)
    fruntypekey = PrimaryKeyField(db_column='fRunTypeKEY')
    fruntypename = CharField(db_column='fRunTypeName', unique=True)

    class Meta:
        db_table = 'RunType'


class Schedule(FactDataModel):
    fdata = CharField(db_column='fData', null=True)
    flastupdate = DateTimeField(db_column='fLastUpdate')
    fmeasurementid = IntegerField(db_column='fMeasurementID')
    fmeasurementtypekey = IntegerField(db_column='fMeasurementTypeKey')
    fscheduleid = PrimaryKeyField(db_column='fScheduleID')
    fsourcekey = IntegerField(db_column='fSourceKey', null=True)
    fstart = DateTimeField(db_column='fStart')
    fuser = CharField(db_column='fUser')

    class Meta:
        db_table = 'Schedule'
        indexes = (
            (('fstart', 'fmeasurementid'), True),
        )


class SequenceComments(FactDataModel):
    fcomment = CharField(db_column='fComment', null=True)
    fcommentkey = PrimaryKeyField(db_column='fCommentKEY')
    fnight = IntegerField(db_column='fNight')
    fsequenceid = IntegerField(db_column='fSequenceID')
    fuser = CharField(db_column='fUser', null=True)

    class Meta:
        db_table = 'SequenceComments'


class SequenceFileAvailISDCStatus(FactDataModel):
    favailable = DateTimeField(db_column='fAvailable', null=True)
    flastupdate = DateTimeField(db_column='fLastUpdate')
    fnight = IntegerField(db_column='fNight')
    fpriority = IntegerField(db_column='fPriority')
    fprocessingsitekey = IntegerField(db_column='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(db_column='fReturnCode', null=True)
    fsequenceid = IntegerField(db_column='fSequenceID')
    fstarttime = DateTimeField(db_column='fStartTime', null=True)
    fstoptime = DateTimeField(db_column='fStopTime', null=True)

    class Meta:
        db_table = 'SequenceFileAvailISDCStatus'
        indexes = (
            (('fnight', 'fsequenceid'), True),
        )
        primary_key = CompositeKey('fnight', 'fsequenceid')


class SequenceFileAVAILWueStatus(FactDataModel):
    favailable = DateTimeField(db_column='fAvailable', null=True)
    flastupdate = DateTimeField(db_column='fLastUpdate')
    fnight = IntegerField(db_column='fNight')
    fpriority = IntegerField(db_column='fPriority')
    fprocessingsitekey = IntegerField(db_column='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(db_column='fReturnCode', null=True)
    fsequenceid = IntegerField(db_column='fSequenceID')
    fstarttime = DateTimeField(db_column='fStartTime', null=True)
    fstoptime = DateTimeField(db_column='fStopTime', null=True)

    class Meta:
        db_table = 'SequenceFileAvailWueStatus'
        indexes = (
            (('fnight', 'fsequenceid'), True),
        )
        primary_key = CompositeKey('fnight', 'fsequenceid')


class SequenceInfo(FactDataModel):
    fazimuthmax = FloatField(db_column='fAzimuthMax', null=True)
    fazimuthmin = FloatField(db_column='fAzimuthMin', null=True)
    flastupdate = DateTimeField(db_column='fLastUpdate')
    fnight = IntegerField(db_column='fNight')
    fnumevents = IntegerField(db_column='fNumEvents')
    fsequenceduration = IntegerField(db_column='fSequenceDuration')
    fsequenceid = IntegerField(db_column='fSequenceID')
    fsequencestart = DateTimeField(db_column='fSequenceStart')
    fsequencestop = DateTimeField(db_column='fSequenceStop')
    fsourcekey = IntegerField(db_column='fSourceKEY')
    fzenithdistancemax = FloatField(db_column='fZenithDistanceMax', null=True)
    fzenithdistancemin = FloatField(db_column='fZenithDistanceMin', null=True)

    class Meta:
        db_table = 'SequenceInfo'
        indexes = (
            (('fnight', 'fsequenceid'), True),
        )
        primary_key = CompositeKey('fnight', 'fsequenceid')


class Source(FactDataModel):
    fdeclination = FloatField(db_column='fDeclination')
    fepochkey = IntegerField(db_column='fEpochKEY', null=True)
    fflux = FloatField(db_column='fFlux', null=True)
    fistoo = IntegerField(db_column='fIsToO')
    fmagnitude = FloatField(db_column='fMagnitude', null=True)
    frightascension = FloatField(db_column='fRightAscension')
    fslope = FloatField(db_column='fSlope', null=True)
    fsourcekey = PrimaryKeyField(db_column='fSourceKEY')
    fsourcename = CharField(db_column='fSourceName')
    fsourcetypekey = IntegerField(db_column='fSourceTypeKey', index=True)
    fwobbleangle0 = IntegerField(db_column='fWobbleAngle0')
    fwobbleangle1 = IntegerField(db_column='fWobbleAngle1')
    fwobbleoffset = FloatField(db_column='fWobbleOffset')

    class Meta:
        db_table = 'Source'


class SourceType(FactDataModel):
    fsourcetype = CharField(db_column='fSourceType', unique=True)
    fsourcetypekey = PrimaryKeyField(db_column='fSourceTypeKEY')
    fsourcetypename = CharField(db_column='fSourceTypeName', unique=True)

    class Meta:
        db_table = 'SourceType'


class StarInfo(FactDataModel):
    flastupdate = DateTimeField(db_column='fLastUpdate')
    fnight = IntegerField(db_column='fNight')
    fsequenceid = IntegerField(db_column='fSequenceID')

    class Meta:
        db_table = 'StarInfo'
        indexes = (
            (('fnight', 'fsequenceid'), True),
        )
        primary_key = CompositeKey('fnight', 'fsequenceid')


class StarStatus(FactDataModel):
    favailable = DateTimeField(db_column='fAvailable', null=True)
    flastupdate = DateTimeField(db_column='fLastUpdate')
    fnight = IntegerField(db_column='fNight')
    fpriority = IntegerField(db_column='fPriority')
    fprocessingsitekey = IntegerField(db_column='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(db_column='fReturnCode', null=True)
    fsequenceid = IntegerField(db_column='fSequenceID')
    fstarttime = DateTimeField(db_column='fStartTime', null=True)
    fstoptime = DateTimeField(db_column='fStopTime', null=True)

    class Meta:
        db_table = 'StarStatus'
        indexes = (
            (('fnight', 'fsequenceid'), True),
        )
        primary_key = CompositeKey('fnight', 'fsequenceid')


class StarWueStatus(FactDataModel):
    favailable = DateTimeField(db_column='fAvailable', null=True)
    flastupdate = DateTimeField(db_column='fLastUpdate')
    fnight = IntegerField(db_column='fNight')
    fpriority = IntegerField(db_column='fPriority')
    fprocessingsitekey = IntegerField(db_column='fProcessingSiteKEY', null=True)
    freturncode = IntegerField(db_column='fReturnCode', null=True)
    fsequenceid = IntegerField(db_column='fSequenceID')
    fstarttime = DateTimeField(db_column='fStartTime', null=True)
    fstoptime = DateTimeField(db_column='fStopTime', null=True)

    class Meta:
        db_table = 'StarWueStatus'
        indexes = (
            (('fnight', 'fsequenceid'), True),
        )
        primary_key = CompositeKey('fnight', 'fsequenceid')


class TPointData(FactDataModel):
    fazencoder = FloatField(db_column='fAzEncoder')
    fazimage = FloatField(db_column='fAzImage')
    faznominal = FloatField(db_column='fAzNominal')
    fdeclination = FloatField(db_column='fDeclination')
    fintensity = FloatField(db_column='fIntensity')
    fmagcatalog = FloatField(db_column='fMagCatalog')
    fmagmeasured = FloatField(db_column='fMagMeasured')
    fnumleds = IntegerField(db_column='fNumLEDs')
    fnumrings = IntegerField(db_column='fNumRings')
    fqualitykey = IntegerField(db_column='fQualityKEY')
    frightascension = FloatField(db_column='fRightAscension')
    fstarname = CharField(db_column='fStarName')
    ftpointkey = PrimaryKeyField(db_column='fTPointKey')
    ftimestamp = DateTimeField(db_column='fTimeStamp')
    fxposcenter = FloatField(db_column='fXPosCenter')
    fxposstar = FloatField(db_column='fXPosStar')
    fyposcenter = FloatField(db_column='fYPosCenter')
    fyposstar = FloatField(db_column='fYPosStar')
    fzdencoder = FloatField(db_column='fZdEncoder')
    fzdimage = FloatField(db_column='fZdImage')
    fzdnominal = FloatField(db_column='fZdNominal')

    class Meta:
        db_table = 'TPointData'


class TPointQuality(FactDataModel):
    fquality = CharField(db_column='fQuality', null=True, unique=True)
    fqualitykey = PrimaryKeyField(db_column='fQualityKEY')
    fqualityname = CharField(db_column='fQualityName', null=True, unique=True)

    class Meta:
        db_table = 'TPointQuality'
