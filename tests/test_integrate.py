"""Test the anomalous Hall conductivity."""
import os

import numpy as np
import pytest
from pytest import approx

import wannierberri as wberri
from conftest import parallel_serial, parallel_ray 
from create_system import create_files_Fe_W90,create_files_GaAs_W90,pythtb_Haldane,tbmodels_Haldane
from create_system import system_Fe_W90,system_GaAs_W90,system_GaAs_tb,system_Haldane_PythTB,system_Haldane_TBmodels
from compare_result import compare_energyresult


@pytest.fixture
def check_integrate(output_dir,parallel_serial):
    def _inner(system,quantities,fout_name,Efermi,comparer,
               parallel=parallel_serial,
               grid_param={'NK':[6,6,6],'NKFFT':[3,3,3]}, adpt_num_iter=0,
               additional_parameters={}, global_parameters={},
               suffix="", suffix_ref="",
               extra_precision={} ):

        grid = wberri.Grid(system, **grid_param)
        result = wberri.integrate(system,
                grid = grid,
                Efermi = Efermi,
                smearEf = 600.0,
    #            omega = omega,
                quantities = quantities,
                parallel=parallel,
                adpt_num_iter = adpt_num_iter,
                parameters = additional_parameters,
                global_parameters = global_parameters,
                fout_name = os.path.join(output_dir, fout_name),
                suffix=suffix,
                restart = False,
                )
        if len(suffix)>0:
            suffix="-"+suffix
        if len(suffix_ref)>0:
            suffix_ref="-"+suffix_ref

        for quant in quantities:
            data=result.results.get(quant).data
            assert data.shape[0] == len(Efermi)
            assert np.all( np.array(data.shape[1:]) == 3)
            prec=extra_precision[quant] if quant in extra_precision else None
            comparer(fout_name, quant+suffix,  adpt_num_iter , suffix_ref=compare_quant(quant)+suffix_ref ,precision=prec )
    return _inner

@pytest.fixture(scope="session")
def Efermi_Fe():
    return np.linspace(17,18,11)


@pytest.fixture(scope="module")
def Efermi_GaAs():
    return np.linspace(7,9,11)

@pytest.fixture(scope="module")
def Efermi_Haldane():
    return np.linspace(-3,3,11)

@pytest.fixture(scope="session")
def quantities_Fe():
    return  ['ahc','ahc_ocean','dos','cumdos'  ,'conductivity_ohmic','conductivity_ohmic_fsurf']

@pytest.fixture(scope="module")
def quantities_Haldane():
    return  ['ahc','ahc_ocean','dos','conductivity_ohmic']

@pytest.fixture(scope="module")
def quantities_GaAs():
    return  ["berry_dipole","berry_dipole_ocean","berry_dipole_fsurf"]


def compare_quant(quant):
    compare= {'ahc_ocean':'ahc',"berry_dipole_ocean":"berry_dipole"}
    if quant in compare:
        return compare[quant]
    else:
        return quant


def test_Fe(check_integrate,system_Fe_W90, compare_energyresult,quantities_Fe,Efermi_Fe):
    """Test anomalous Hall conductivity , ohmic conductivity, dos, cumdos"""
    check_integrate(system_Fe_W90 , quantities_Fe , fout_name="berry_Fe_W90" , suffix="" , Efermi=Efermi_Fe , comparer=compare_energyresult,
               global_parameters = {'use_symmetry' : False} )


def test_Fe_wcc(check_integrate,system_Fe_W90, compare_energyresult,quantities_Fe,Efermi_Fe):
    """Test anomalous Hall conductivity , ohmic conductivity, dos, cumdos"""
    check_integrate(system_Fe_W90 , quantities_Fe , fout_name="berry_Fe_W90" , suffix="wcc" , Efermi=Efermi_Fe , comparer=compare_energyresult , 
                global_parameters = {'use_wcc_phase':True, 'use_symmetry' : False})

def test_Fe_sym(check_integrate,system_Fe_W90, compare_energyresult,quantities_Fe,Efermi_Fe):
    """Test anomalous Hall conductivity , ohmic conductivity, dos, cumdos"""
    check_integrate(system_Fe_W90 , quantities_Fe , fout_name="berry_Fe_W90" , suffix="sym" , suffix_ref="sym", Efermi=Efermi_Fe , comparer=compare_energyresult,
               global_parameters = {'use_symmetry' : True} )


def test_GaAs(check_integrate,system_GaAs_W90, compare_energyresult,quantities_GaAs,Efermi_GaAs):
    """Test berry dipole"""
    check_integrate(system_GaAs_W90 , quantities_GaAs , fout_name="berry_GaAs_W90" , suffix="" , Efermi=Efermi_GaAs , comparer=compare_energyresult ,
               global_parameters = {'use_wcc_phase':False,'degen_thresh':0.005,'use_symmetry' : False },
                  extra_precision = {"berry_dipole_fsurf":1e-6} )   # This is a low precision for the nonabelian thing, not sure if it does not indicate a problem, or is a gauge-dependent thing

def test_GaAs_tb(check_integrate,system_GaAs_tb, compare_energyresult,quantities_GaAs,Efermi_GaAs):
    """Test berry dipole"""
    check_integrate(system_GaAs_tb , quantities_GaAs , fout_name="berry_GaAs_tb" , suffix="" , Efermi=Efermi_GaAs , comparer=compare_energyresult ,
               global_parameters = {'use_symmetry' : False} ,
                  extra_precision = {"berry_dipole_fsurf":1e-6}  )   # This is a low precision for the nonabelian thing, not sure if it does not indicate a problem, or is a gauge-dependent thing

def test_GaAs_wcc(check_integrate,system_GaAs_W90, compare_energyresult,quantities_GaAs,Efermi_GaAs):
    """Test berry dipole with wcc_phase"""
    check_integrate(system_GaAs_W90 , quantities_GaAs , fout_name="berry_GaAs_W90" , suffix="wcc" , Efermi=Efermi_GaAs , comparer=compare_energyresult , 
               global_parameters = {'use_wcc_phase':True,'degen_thresh':0.005 , 'use_symmetry' : False},
                  extra_precision = {"berry_dipole_fsurf":1e-6} )   # This is a low precision for the nonabelian thing, not sure if it does not indicate a problem

def test_GaAs_tb_wcc(check_integrate,system_GaAs_tb, compare_energyresult,quantities_GaAs,Efermi_GaAs):
    """Test berry dipole with wcc_phase"""
    check_integrate(system_GaAs_tb , quantities_GaAs , fout_name="berry_GaAs_tb" , suffix="wcc" , Efermi=Efermi_GaAs , comparer=compare_energyresult,
                    global_parameters = {'use_wcc_phase':True, 'use_symmetry' : False} ,
                  extra_precision = {"berry_dipole_fsurf":1e-6} )   # This is a low precision for the nonabelian thing, not sure if it does not indicate a problem, or is a gauge-dependent thing

    
def test_Haldane_PythTB(check_integrate,system_Haldane_PythTB,compare_energyresult,quantities_Haldane,Efermi_Haldane):
    check_integrate(system_Haldane_PythTB , quantities_Haldane , fout_name="berry_Haldane_pythtb" , suffix="" , Efermi=Efermi_Haldane , comparer=compare_energyresult,
               global_parameters = {'use_symmetry' : False} ,
            grid_param={'NK':[10,10,1], 'NKFFT':[5,5,1]} )

def test_Haldane_TBmodels(check_integrate,system_Haldane_TBmodels,compare_energyresult,quantities_Haldane,Efermi_Haldane):
    check_integrate(system_Haldane_TBmodels , quantities_Haldane , fout_name="berry_Haldane_tbmodels" , suffix="" , Efermi=Efermi_Haldane , comparer=compare_energyresult,
               global_parameters = {'use_symmetry' : False} ,
            grid_param={'NK':[10,10,1], 'NKFFT':[5,5,1]} )

def test_Haldane_PythTB_wcc(check_integrate,system_Haldane_PythTB,compare_energyresult,quantities_Haldane,Efermi_Haldane):
    check_integrate(system_Haldane_PythTB , quantities_Haldane , fout_name="berry_Haldane_pythtb" , suffix="wcc" , Efermi=Efermi_Haldane , comparer=compare_energyresult,
               global_parameters = {'use_symmetry' : False} ,
            grid_param={'NK':[10,10,1], 'NKFFT':[5,5,1]} )

def test_Haldane_TBmodels_wcc(check_integrate,system_Haldane_TBmodels,compare_energyresult,quantities_Haldane,Efermi_Haldane):
    check_integrate(system_Haldane_TBmodels , quantities_Haldane , fout_name="berry_Haldane_tbmodels" , suffix="wcc" , Efermi=Efermi_Haldane , comparer=compare_energyresult,
               global_parameters = {'use_symmetry' : False, 'use_wcc_phase':True} ,
               grid_param={'NK':[10,10,1], 'NKFFT':[5,5,1]} )


def test_Haldane_PythTB_sym(check_integrate,system_Haldane_PythTB,compare_energyresult,quantities_Haldane,Efermi_Haldane):
    check_integrate(system_Haldane_PythTB , quantities_Haldane , fout_name="berry_Haldane_pythtb" , suffix="sym" , suffix_ref="",
            Efermi=Efermi_Haldane , comparer=compare_energyresult,
               global_parameters = {'use_symmetry' : True} ,
            grid_param={'NK':[10,10,1], 'NKFFT':[5,5,1]} )

def test_Haldane_TBmodels_sym(check_integrate,system_Haldane_TBmodels,compare_energyresult,quantities_Haldane,Efermi_Haldane):
    check_integrate(system_Haldane_TBmodels , quantities_Haldane , fout_name="berry_Haldane_tbmodels" , suffix="sym" , suffix_ref="",
            Efermi=Efermi_Haldane , comparer=compare_energyresult,
               global_parameters = {'use_symmetry' : True} ,
            grid_param={'NK':[10,10,1], 'NKFFT':[5,5,1]} )

def test_Haldane_TBmodels_sym_refine(check_integrate,system_Haldane_TBmodels,compare_energyresult,quantities_Haldane,Efermi_Haldane):
    check_integrate(system_Haldane_TBmodels , quantities_Haldane , fout_name="berry_Haldane_tbmodels" , suffix="sym" , suffix_ref="sym",
            Efermi=Efermi_Haldane , comparer=compare_energyresult, adpt_num_iter=1,
               global_parameters = {'use_symmetry' : True} ,
            grid_param={'NK':[10,10,1], 'NKFFT':[5,5,1]} )


def test_Fe_sym_refine(check_integrate,system_Fe_W90, compare_energyresult,quantities_Fe,Efermi_Fe):
    """Test anomalous Hall conductivity , ohmic conductivity, dos, cumdos"""
    check_integrate(system_Fe_W90 , quantities_Fe , fout_name="berry_Fe_W90" , 
                  adpt_num_iter=1,
                  global_parameters = {'use_symmetry' : True} ,
                  suffix="sym" , suffix_ref="sym", Efermi=Efermi_Fe , comparer=compare_energyresult )


def test_Fe_parallel_ray(check_integrate, system_Fe_W90, compare_energyresult,quantities_Fe,Efermi_Fe,
      parallel_ray):
    """Test anomalous Hall conductivity , ohmic conductivity, dos, cumdos in parallel with ray"""
    check_integrate(system_Fe_W90 , quantities_Fe , fout_name="berry_Fe_W90" , suffix="paral-ray-4" , suffix_ref="",  Efermi=Efermi_Fe , comparer=compare_energyresult,parallel=parallel_ray,
                              global_parameters = {'use_symmetry' : False} ,
)
