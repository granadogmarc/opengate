//
// ********************************************************************
// * License and Disclaimer                                           *
// *                                                                  *
// * The  Geant4 software  is  copyright of the Copyright Holders  of *
// * the Geant4 Collaboration.  It is provided  under  the terms  and *
// * conditions of the Geant4 Software License,  included in the file *
// * LICENSE and available at  http://cern.ch/geant4/license .  These *
// * include a list of copyright holders.                             *
// *                                                                  *
// * Neither the authors of this software system, nor their employing *
// * institutes,nor the agencies providing financial support for this *
// * work  make  any representation or  warranty, express or implied, *
// * regarding  this  software system or assume any liability for its *
// * use.  Please see the license in the file  LICENSE  and URL above *
// * for the full disclaimer and the limitation of liability.         *
// *                                                                  *
// * This  code  implementation is the result of  the  scientific and *
// * technical work of the GEANT4 collaboration.                      *
// * By using,  copying,  modifying or  distributing the software (or *
// * any work based  on the software)  you  agree  to acknowledge its *
// * use  in  resulting  scientific  publications,  and indicate your *
// * acceptance of all terms of the Geant4 Software license.          *
// ********************************************************************
//
//
/// \file GateOptneBremSplitting.cc
/// \brief Implementation of the GateOptneBremSplitting class

#include "GateOptneBremSplitting.h"
#include "G4BiasingProcessInterface.hh"

#include "G4ComptonScattering.hh"
#include "G4DynamicParticle.hh"
#include "G4Exception.hh"
#include "G4Gamma.hh"
#include "G4GammaConversion.hh"
#include "G4ParticleChange.hh"
#include "GateOptnVGenericSplitting.h"
#include "G4ParticleChangeForGamma.hh"
#include "G4ParticleChangeForLoss.hh"
#include "G4PhotoElectricEffect.hh"
#include "G4ProcessType.hh"
#include "G4RayleighScattering.hh"
#include "G4SystemOfUnits.hh"
#include "G4TrackStatus.hh"
#include "G4TrackingManager.hh"
#include "G4VEmProcess.hh"
#include <memory>

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

GateOptneBremSplitting::
    GateOptneBremSplitting(G4String name)
    :GateOptnVGenericSplitting(name), fParticleChange() {}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

GateOptneBremSplitting::
    ~GateOptneBremSplitting() {}

G4VParticleChange *
GateOptneBremSplitting::ApplyFinalStateBiasing(const G4BiasingProcessInterface *callingProcess, const G4Track *track, const G4Step *step, G4bool &) {

  G4int splittingFactor = ceil(fSplittingFactor);
  G4double survivalProbabilitySplitting = 1 - (splittingFactor - fSplittingFactor) / splittingFactor;
  G4VParticleChange* processFinalState = callingProcess->GetWrappedProcess()->PostStepDoIt(*track, *step);
  if ( fSplittingFactor == 1 ) return processFinalState;
  if ( processFinalState->GetNumberOfSecondaries() == 0 )  return processFinalState;

  TrackInitializationChargedParticle(&fParticleChange,processFinalState, track,fSplittingFactor);
  

  processFinalState->Clear(); 


  G4int nCalls = 1;
  while ( nCalls <= fSplittingFactor ){ 
    G4double splittingProbability = G4UniformRand();
    if (splittingProbability <= survivalProbabilitySplitting || survivalProbabilitySplitting == 1) {
      processFinalState = callingProcess->GetWrappedProcess()->PostStepDoIt(*track, *step);
      if ( processFinalState->GetNumberOfSecondaries() >= 1 ) {
        for(int i =0; i < processFinalState->GetNumberOfSecondaries();i++){
          G4double gammaWeight = track->GetWeight() / fSplittingFactor;
          G4Track* gammaTrack = processFinalState->GetSecondary(i);
          if (fRussianRouletteForAngle == true){
            G4double weightToApply = RussianRouletteForAngleSurvival(gammaTrack->GetMomentumDirection(),fVectorDirector,fMaxTheta,fSplittingFactor);
            if (weightToApply != 0){
              gammaWeight = gammaWeight * weightToApply;
              gammaTrack->SetWeight( gammaWeight);
              fParticleChange.AddSecondary( gammaTrack );
            }
          }
          else {
            gammaTrack->SetWeight( gammaWeight);
            fParticleChange.AddSecondary(gammaTrack);
          }
        }
      }
      processFinalState->Clear();
    }
    nCalls++;
    }
    return &fParticleChange;
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......